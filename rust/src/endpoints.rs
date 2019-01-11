//! API server endpoint request/response wrappers
//!
//! These mostly deal with type conversion between internal function signatures and API-defined
//! response types (mapping to HTTP statuses. Some contain actual endpoint implementations, but
//! most implementation lives in the server module.

// using closures as a Result/? hack
#![allow(clippy::redundant_closure_call)]

use crate::auth::*;
use crate::database_models::EntityEditRow;
use crate::editing::*;
use crate::entity_crud::{EntityCrud, ExpandFlags, HideFlags};
use crate::errors::*;
use crate::identifiers::*;
use crate::server::*;
use diesel::Connection;
use fatcat_api_spec::models;
use fatcat_api_spec::models::*;
use fatcat_api_spec::*;
use futures::{self, Future};
use sentry::integrations::failure::capture_fail;
use std::str::FromStr;
use uuid::{self, Uuid};
use cadence::prelude::*;

// This makes response matching below *much* more terse
use crate::errors::FatcatError::*;

// I heard you liked macros, so I use macros in your macros
macro_rules! generic_auth_err_responses {
    ($val:ident, $resp_type:ident) => {
        //use crate::errors::FatcatError::*;
        match $val {
            NotFound(_, _) => $resp_type::NotFound($val.into()),
            InvalidCredentials(_) | InsufficientPrivileges(_) => $resp_type::Forbidden($val.into()),
            DatabaseError(_) | InternalError(_) => {
                error!("{}", $val);
                capture_fail(&$val);
                $resp_type::GenericError($val.into())
            }
            _ => $resp_type::BadRequest($val.into()),
        }
    };
}

macro_rules! generic_err_responses {
    ($val:ident, $resp_type:ident) => {
        //use crate::errors::FatcatError::*;
        match $val {
            NotFound(_, _) => $resp_type::NotFound($val.into()),
            DatabaseError(_) | InternalError(_) => {
                error!("{}", $val);
                capture_fail(&$val);
                $resp_type::GenericError($val.into())
            }
            _ => $resp_type::BadRequest($val.into()),
        }
    };
}

/// Helper for generating wrappers (which return "Box::new(futures::done(Ok(BLAH)))" like the
/// codegen fatcat-api-spec code wants) that call through to actual helpers (which have simple
/// Result<> return types)
macro_rules! wrap_entity_handlers {
    // Would much rather just have entity ident, then generate the other fields from that, but Rust
    // stable doesn't have a mechanism to "concat" or generate new identifiers in macros, at least
    // in the context of defining new functions.
    // The only stable approach I know of would be: https://github.com/dtolnay/mashup
    ($get_fn:ident, $get_resp:ident, $post_fn:ident, $post_resp:ident, $post_batch_fn:ident,
    $post_batch_handler:ident, $post_batch_resp:ident, $update_fn:ident, $update_resp:ident,
    $delete_fn:ident, $delete_resp:ident, $get_history_fn:ident, $get_history_resp:ident,
    $get_edit_fn:ident, $get_edit_resp:ident, $delete_edit_fn:ident, $delete_edit_resp:ident,
    $get_rev_fn:ident, $get_rev_resp:ident, $get_redirects_fn:ident, $get_redirects_resp:ident,
    $model:ident) => {

        fn $get_fn(
            &self,
            ident: String,
            expand: Option<String>,
            hide: Option<String>,
            _context: &Context,
        ) -> Box<Future<Item = $get_resp, Error = ApiError> + Send> {
            let conn = self.db_pool.get().expect("db_pool error");
            // No transaction for GET
            let ret = match (|| {
                let entity_id = FatcatId::from_str(&ident)?;
                let hide_flags = match hide {
                    None => HideFlags::none(),
                    Some(param) => HideFlags::from_str(&param)?,
                };
                match expand {
                    None => $model::db_get(&conn, entity_id, hide_flags),
                    Some(param) => {
                        let expand_flags = ExpandFlags::from_str(&param)?;
                        let mut entity = $model::db_get(&conn, entity_id, hide_flags)?;
                        entity.db_expand(&conn, expand_flags)?;
                        Ok(entity)
                    },
                }
            })().map_err(|e| FatcatError::from(e)) {
                Ok(entity) =>
                    $get_resp::FoundEntity(entity),
                Err(fe) => generic_err_responses!(fe, $get_resp),
            };
            Box::new(futures::done(Ok(ret)))
        }

        fn $post_fn(
            &self,
            entity: models::$model,
            editgroup_id: String,
            context: &Context,
        ) -> Box<Future<Item = $post_resp, Error = ApiError> + Send> {
            let conn = self.db_pool.get().expect("db_pool error");
            let ret = match conn.transaction(|| {
                let editgroup_id = FatcatId::from_str(&editgroup_id)?;
                let auth_context = self.auth_confectionary.require_auth(&conn, &context.auth_data, Some(stringify!($post_fn)))?;
                auth_context.require_role(FatcatRole::Editor)?;
                auth_context.require_editgroup(&conn, editgroup_id)?;
                let edit_context = make_edit_context(&conn, auth_context.editor_id, Some(editgroup_id), false)?;
                edit_context.check(&conn)?;
                entity.db_create(&conn, &edit_context)?.into_model()
            }).map_err(|e| FatcatError::from(e)) {
                Ok(edit) => {
                    self.metrics.incr("entities.created").ok();
                    $post_resp::CreatedEntity(edit)
                },
                Err(fe) => generic_auth_err_responses!(fe, $post_resp),
            };
            Box::new(futures::done(Ok(ret)))
        }

        fn $post_batch_fn(
            &self,
            entity_list: &Vec<models::$model>,
            autoaccept: Option<bool>,
            editgroup_id: Option<String>,
            context: &Context,
        ) -> Box<Future<Item = $post_batch_resp, Error = ApiError> + Send> {
            let conn = self.db_pool.get().expect("db_pool error");
            let ret = match conn.transaction(|| {
                let auth_context = self.auth_confectionary.require_auth(&conn, &context.auth_data, Some(stringify!($post_batch_fn)))?;
                auth_context.require_role(FatcatRole::Editor)?;
                let editgroup_id = if let Some(s) = editgroup_id {
                    let eg_id = FatcatId::from_str(&s)?;
                    auth_context.require_editgroup(&conn, eg_id)?;
                    Some(eg_id)
                } else { None };
                self.$post_batch_handler(&conn, entity_list, autoaccept.unwrap_or(false), auth_context.editor_id, editgroup_id)
            }).map_err(|e| FatcatError::from(e)) {
                Ok(edits) => {
                    self.metrics.count("entities.created", edits.len() as i64).ok();
                    if let Some(true) = autoaccept {
                        self.metrics.incr("editgroup.created").ok();
                        self.metrics.incr("editgroup.accepted").ok();
                    };
                    $post_batch_resp::CreatedEntities(edits)
                },
                Err(fe) => generic_auth_err_responses!(fe, $post_batch_resp),
            };
            Box::new(futures::done(Ok(ret)))
        }

        fn $update_fn(
            &self,
            ident: String,
            entity: models::$model,
            editgroup_id: String,
            context: &Context,
        ) -> Box<Future<Item = $update_resp, Error = ApiError> + Send> {
            let conn = self.db_pool.get().expect("db_pool error");
            let ret = match conn.transaction(|| {
                let editgroup_id = FatcatId::from_str(&editgroup_id)?;
                let auth_context = self.auth_confectionary.require_auth(&conn, &context.auth_data, Some(stringify!($update_fn)))?;
                auth_context.require_role(FatcatRole::Editor)?;
                let entity_id = FatcatId::from_str(&ident)?;
                auth_context.require_editgroup(&conn, editgroup_id)?;
                let edit_context = make_edit_context(&conn, auth_context.editor_id, Some(editgroup_id), false)?;
                edit_context.check(&conn)?;
                entity.db_update(&conn, &edit_context, entity_id)?.into_model()
            }).map_err(|e| FatcatError::from(e)) {
                Ok(edit) => {
                    self.metrics.incr("entities.updated").ok();
                    $update_resp::UpdatedEntity(edit)
                },
                Err(fe) => generic_auth_err_responses!(fe, $update_resp),
            };
            Box::new(futures::done(Ok(ret)))
        }

        fn $delete_fn(
            &self,
            ident: String,
            editgroup_id: String,
            context: &Context,
        ) -> Box<Future<Item = $delete_resp, Error = ApiError> + Send> {
            let conn = self.db_pool.get().expect("db_pool error");
            let ret = match conn.transaction(|| {
                let editgroup_id = FatcatId::from_str(&editgroup_id)?;
                let auth_context = self.auth_confectionary.require_auth(&conn, &context.auth_data, Some(stringify!($delete_fn)))?;
                auth_context.require_role(FatcatRole::Editor)?;
                let entity_id = FatcatId::from_str(&ident)?;
                auth_context.require_editgroup(&conn, editgroup_id)?;
                let edit_context = make_edit_context(&conn, auth_context.editor_id, Some(editgroup_id), false)?;
                edit_context.check(&conn)?;
                $model::db_delete(&conn, &edit_context, entity_id)?.into_model()
            }).map_err(|e| FatcatError::from(e)) {
                Ok(edit) => {
                    self.metrics.incr("entities.deleted").ok();
                    $delete_resp::DeletedEntity(edit)
                },
                Err(fe) => generic_auth_err_responses!(fe, $delete_resp),
            };
            Box::new(futures::done(Ok(ret)))
        }

        fn $get_history_fn(
            &self,
            ident: String,
            limit: Option<i64>,
            _context: &Context,
        ) -> Box<Future<Item = $get_history_resp, Error = ApiError> + Send> {
            let conn = self.db_pool.get().expect("db_pool error");
            // No transaction for GET?
            let ret = match (|| {
                let entity_id = FatcatId::from_str(&ident)?;
                $model::db_get_history(&conn, entity_id, limit)
            })().map_err(|e| FatcatError::from(e)) {
                Ok(history) =>
                    $get_history_resp::FoundEntityHistory(history),
                Err(fe) => generic_err_responses!(fe, $get_history_resp),
            };
            Box::new(futures::done(Ok(ret)))
        }

        fn $get_rev_fn(
            &self,
            rev_id: String,
            expand: Option<String>,
            hide: Option<String>,
            _context: &Context,
        ) -> Box<Future<Item = $get_rev_resp, Error = ApiError> + Send> {
            let conn = self.db_pool.get().expect("db_pool error");
            // No transaction for GET?
            let ret = match (|| {
                let rev_id = Uuid::from_str(&rev_id)?;
                let hide_flags = match hide {
                    None => HideFlags::none(),
                    Some(param) => HideFlags::from_str(&param)?,
                };
                match expand {
                    None => $model::db_get_rev(&conn, rev_id, hide_flags),
                    Some(param) => {
                        let expand_flags = ExpandFlags::from_str(&param)?;
                        let mut entity = $model::db_get_rev(&conn, rev_id, hide_flags)?;
                        entity.db_expand(&conn, expand_flags)?;
                        Ok(entity)
                    },
                }
            })().map_err(|e| FatcatError::from(e)) {
                Ok(entity) =>
                    $get_rev_resp::FoundEntityRevision(entity),
                Err(fe) => generic_err_responses!(fe, $get_rev_resp),
            };
            Box::new(futures::done(Ok(ret)))
        }

        fn $get_edit_fn(
            &self,
            edit_id: String,
            _context: &Context,
        ) -> Box<Future<Item = $get_edit_resp, Error = ApiError> + Send> {
            let conn = self.db_pool.get().expect("db_pool error");
            // No transaction for GET?
            let ret = match (|| {
                let edit_id = Uuid::from_str(&edit_id)?;
                $model::db_get_edit(&conn, edit_id)?.into_model()
            })().map_err(|e| FatcatError::from(e)) {
                Ok(edit) =>
                    $get_edit_resp::FoundEdit(edit),
                Err(fe) => generic_err_responses!(fe, $get_edit_resp),
            };
            Box::new(futures::done(Ok(ret)))
        }

        fn $delete_edit_fn(
            &self,
            edit_id: String,
            context: &Context,
        ) -> Box<Future<Item = $delete_edit_resp, Error = ApiError> + Send> {
            let conn = self.db_pool.get().expect("db_pool error");
            let ret = match conn.transaction(|| {
                let edit_id = Uuid::from_str(&edit_id)?;
                let auth_context = self.auth_confectionary.require_auth(&conn, &context.auth_data, Some(stringify!($delete_edit_fn)))?;
                auth_context.require_role(FatcatRole::Editor)?;
                let edit = $model::db_get_edit(&conn, edit_id)?;
                auth_context.require_editgroup(&conn, FatcatId::from_uuid(&edit.editgroup_id))?;
                $model::db_delete_edit(&conn, edit_id)
            }).map_err(|e| FatcatError::from(e)) {
                Ok(()) =>
                    $delete_edit_resp::DeletedEdit(Success {
                        success: true,
                        message: format!("Successfully deleted work-in-progress {} edit: {}", stringify!($model), edit_id)
                }),
                Err(fe) => generic_auth_err_responses!(fe, $delete_edit_resp),
            };
            Box::new(futures::done(Ok(ret)))
        }

        fn $get_redirects_fn(
            &self,
            ident: String,
            _context: &Context,
        ) -> Box<Future<Item = $get_redirects_resp, Error = ApiError> + Send> {
            let conn = self.db_pool.get().expect("db_pool error");
            // No transaction for GET?
            let ret = match (|| {
                let entity_id = FatcatId::from_str(&ident)?;
                let redirects: Vec<FatcatId> = $model::db_get_redirects(&conn, entity_id)?;
                Ok(redirects.into_iter().map(|fcid| fcid.to_string()).collect())
            })().map_err(|e: Error| FatcatError::from(e)) {
                Ok(redirects) =>
                    $get_redirects_resp::FoundEntityRedirects(redirects),
                Err(fe) => generic_err_responses!(fe, $get_redirects_resp),
            };
            Box::new(futures::done(Ok(ret)))
        }

    }
}

macro_rules! wrap_lookup_handler {
    ($get_fn:ident, $get_handler:ident, $get_resp:ident, $idname:ident) => {
        fn $get_fn(
            &self,
            $idname: Option<String>,
            wikidata_qid: Option<String>,
            expand: Option<String>,
            hide: Option<String>,
            _context: &Context,
        ) -> Box<Future<Item = $get_resp, Error = ApiError> + Send> {
            let conn = self.db_pool.get().expect("db_pool error");
            let expand_flags = match expand {
                None => ExpandFlags::none(),
                Some(param) => ExpandFlags::from_str(&param).unwrap(),
            };
            let hide_flags = match hide {
                None => HideFlags::none(),
                Some(param) => HideFlags::from_str(&param).unwrap(),
            };
            // No transaction for GET
            let ret = match self.$get_handler(&conn, &$idname, &wikidata_qid, expand_flags, hide_flags).map_err(|e| FatcatError::from(e)) {
                Ok(entity) =>
                    $get_resp::FoundEntity(entity),
                Err(fe) => generic_err_responses!(fe, $get_resp),
            };
            Box::new(futures::done(Ok(ret)))
        }
    }
}

macro_rules! wrap_fcid_handler {
    ($get_fn:ident, $get_handler:ident, $get_resp:ident) => {
        fn $get_fn(
            &self,
            id: String,
            _context: &Context,
        ) -> Box<Future<Item = $get_resp, Error = ApiError> + Send> {
            let conn = self.db_pool.get().expect("db_pool error");
            // No transaction for GET
            let ret = match (|| {
                let fcid = FatcatId::from_str(&id)?;
                self.$get_handler(&conn, fcid)
            })().map_err(|e| FatcatError::from(e)) {
                Ok(entity) =>
                    $get_resp::Found(entity),
                Err(fe) => generic_err_responses!(fe, $get_resp),
            };
            Box::new(futures::done(Ok(ret)))
        }
    }
}

macro_rules! wrap_fcid_hide_handler {
    ($get_fn:ident, $get_handler:ident, $get_resp:ident) => {
        fn $get_fn(
            &self,
            id: String,
            hide: Option<String>,
            _context: &Context,
        ) -> Box<Future<Item = $get_resp, Error = ApiError> + Send> {
            let conn = self.db_pool.get().expect("db_pool error");
            // No transaction for GET
            let ret = match (|| {
                let fcid = FatcatId::from_str(&id)?;
                let hide_flags = match hide {
                    None => HideFlags::none(),
                    Some(param) => HideFlags::from_str(&param)?,
                };
                self.$get_handler(&conn, fcid, hide_flags)
            })().map_err(|e| FatcatError::from(e)) {
                Ok(entity) =>
                    $get_resp::Found(entity),
                Err(fe) => generic_err_responses!(fe, $get_resp),
            };
            Box::new(futures::done(Ok(ret)))
        }
    }
}

impl Api for Server {
    wrap_entity_handlers!(
        get_container,
        GetContainerResponse,
        create_container,
        CreateContainerResponse,
        create_container_batch,
        create_container_batch_handler,
        CreateContainerBatchResponse,
        update_container,
        UpdateContainerResponse,
        delete_container,
        DeleteContainerResponse,
        get_container_history,
        GetContainerHistoryResponse,
        get_container_edit,
        GetContainerEditResponse,
        delete_container_edit,
        DeleteContainerEditResponse,
        get_container_revision,
        GetContainerRevisionResponse,
        get_container_redirects,
        GetContainerRedirectsResponse,
        ContainerEntity
    );

    wrap_entity_handlers!(
        get_creator,
        GetCreatorResponse,
        create_creator,
        CreateCreatorResponse,
        create_creator_batch,
        create_creator_batch_handler,
        CreateCreatorBatchResponse,
        update_creator,
        UpdateCreatorResponse,
        delete_creator,
        DeleteCreatorResponse,
        get_creator_history,
        GetCreatorHistoryResponse,
        get_creator_edit,
        GetCreatorEditResponse,
        delete_creator_edit,
        DeleteCreatorEditResponse,
        get_creator_revision,
        GetCreatorRevisionResponse,
        get_creator_redirects,
        GetCreatorRedirectsResponse,
        CreatorEntity
    );
    wrap_entity_handlers!(
        get_file,
        GetFileResponse,
        create_file,
        CreateFileResponse,
        create_file_batch,
        create_file_batch_handler,
        CreateFileBatchResponse,
        update_file,
        UpdateFileResponse,
        delete_file,
        DeleteFileResponse,
        get_file_history,
        GetFileHistoryResponse,
        get_file_edit,
        GetFileEditResponse,
        delete_file_edit,
        DeleteFileEditResponse,
        get_file_revision,
        GetFileRevisionResponse,
        get_file_redirects,
        GetFileRedirectsResponse,
        FileEntity
    );
    wrap_entity_handlers!(
        get_fileset,
        GetFilesetResponse,
        create_fileset,
        CreateFilesetResponse,
        create_fileset_batch,
        create_fileset_batch_handler,
        CreateFilesetBatchResponse,
        update_fileset,
        UpdateFilesetResponse,
        delete_fileset,
        DeleteFilesetResponse,
        get_fileset_history,
        GetFilesetHistoryResponse,
        get_fileset_edit,
        GetFilesetEditResponse,
        delete_fileset_edit,
        DeleteFilesetEditResponse,
        get_fileset_revision,
        GetFilesetRevisionResponse,
        get_fileset_redirects,
        GetFilesetRedirectsResponse,
        FilesetEntity
    );
    wrap_entity_handlers!(
        get_webcapture,
        GetWebcaptureResponse,
        create_webcapture,
        CreateWebcaptureResponse,
        create_webcapture_batch,
        create_webcapture_batch_handler,
        CreateWebcaptureBatchResponse,
        update_webcapture,
        UpdateWebcaptureResponse,
        delete_webcapture,
        DeleteWebcaptureResponse,
        get_webcapture_history,
        GetWebcaptureHistoryResponse,
        get_webcapture_edit,
        GetWebcaptureEditResponse,
        delete_webcapture_edit,
        DeleteWebcaptureEditResponse,
        get_webcapture_revision,
        GetWebcaptureRevisionResponse,
        get_webcapture_redirects,
        GetWebcaptureRedirectsResponse,
        WebcaptureEntity
    );
    wrap_entity_handlers!(
        get_release,
        GetReleaseResponse,
        create_release,
        CreateReleaseResponse,
        create_release_batch,
        create_release_batch_handler,
        CreateReleaseBatchResponse,
        update_release,
        UpdateReleaseResponse,
        delete_release,
        DeleteReleaseResponse,
        get_release_history,
        GetReleaseHistoryResponse,
        get_release_edit,
        GetReleaseEditResponse,
        delete_release_edit,
        DeleteReleaseEditResponse,
        get_release_revision,
        GetReleaseRevisionResponse,
        get_release_redirects,
        GetReleaseRedirectsResponse,
        ReleaseEntity
    );
    wrap_entity_handlers!(
        get_work,
        GetWorkResponse,
        create_work,
        CreateWorkResponse,
        create_work_batch,
        create_work_batch_handler,
        CreateWorkBatchResponse,
        update_work,
        UpdateWorkResponse,
        delete_work,
        DeleteWorkResponse,
        get_work_history,
        GetWorkHistoryResponse,
        get_work_edit,
        GetWorkEditResponse,
        delete_work_edit,
        DeleteWorkEditResponse,
        get_work_revision,
        GetWorkRevisionResponse,
        get_work_redirects,
        GetWorkRedirectsResponse,
        WorkEntity
    );

    wrap_lookup_handler!(
        lookup_container,
        lookup_container_handler,
        LookupContainerResponse,
        issnl
    );
    wrap_lookup_handler!(
        lookup_creator,
        lookup_creator_handler,
        LookupCreatorResponse,
        orcid
    );

    wrap_fcid_hide_handler!(
        get_release_files,
        get_release_files_handler,
        GetReleaseFilesResponse
    );
    wrap_fcid_hide_handler!(
        get_release_filesets,
        get_release_filesets_handler,
        GetReleaseFilesetsResponse
    );
    wrap_fcid_hide_handler!(
        get_release_webcaptures,
        get_release_webcaptures_handler,
        GetReleaseWebcapturesResponse
    );
    wrap_fcid_hide_handler!(
        get_work_releases,
        get_work_releases_handler,
        GetWorkReleasesResponse
    );
    wrap_fcid_hide_handler!(
        get_creator_releases,
        get_creator_releases_handler,
        GetCreatorReleasesResponse
    );
    wrap_fcid_handler!(get_editor, get_editor_handler, GetEditorResponse);
    wrap_fcid_handler!(
        get_editor_changelog,
        get_editor_changelog_handler,
        GetEditorChangelogResponse
    );

    fn lookup_file(
        &self,
        md5: Option<String>,
        sha1: Option<String>,
        sha256: Option<String>,
        expand: Option<String>,
        hide: Option<String>,
        _context: &Context,
    ) -> Box<Future<Item = LookupFileResponse, Error = ApiError> + Send> {
        let conn = self.db_pool.get().expect("db_pool error");
        let expand_flags = match expand {
            None => ExpandFlags::none(),
            Some(param) => ExpandFlags::from_str(&param).unwrap(),
        };
        let hide_flags = match hide {
            None => HideFlags::none(),
            Some(param) => HideFlags::from_str(&param).unwrap(),
        };
        // No transaction for GET
        let ret = match self
            .lookup_file_handler(&conn, &md5, &sha1, &sha256, expand_flags, hide_flags)
            .map_err(|e| FatcatError::from(e))
        {
            Ok(entity) => LookupFileResponse::FoundEntity(entity),
            Err(fe) => generic_err_responses!(fe, LookupFileResponse),
        };
        Box::new(futures::done(Ok(ret)))
    }

    fn lookup_release(
        &self,
        doi: Option<String>,
        wikidata_qid: Option<String>,
        isbn13: Option<String>,
        pmid: Option<String>,
        pmcid: Option<String>,
        core_id: Option<String>,
        expand: Option<String>,
        hide: Option<String>,
        _context: &Context,
    ) -> Box<Future<Item = LookupReleaseResponse, Error = ApiError> + Send> {
        let conn = self.db_pool.get().expect("db_pool error");
        let expand_flags = match expand {
            None => ExpandFlags::none(),
            Some(param) => ExpandFlags::from_str(&param).unwrap(),
        };
        let hide_flags = match hide {
            None => HideFlags::none(),
            Some(param) => HideFlags::from_str(&param).unwrap(),
        };
        // No transaction for GET
        let ret = match self
            .lookup_release_handler(
                &conn,
                &doi,
                &wikidata_qid,
                &isbn13,
                &pmid,
                &pmcid,
                &core_id,
                expand_flags,
                hide_flags,
            )
            .map_err(|e| FatcatError::from(e))
        {
            Ok(entity) => LookupReleaseResponse::FoundEntity(entity),
            // TODO: ensure good 'Not Found" error message here
            // (was: "Not found: {:?} / {:?} / {:?} / {:?} / {:?} / {:?}", doi, wikidata_qid, isbn13, pmid, pmcid, core_id
            Err(fe) => generic_err_responses!(fe, LookupReleaseResponse),
        };
        Box::new(futures::done(Ok(ret)))
    }

    /// For now, only implements updating username
    fn update_editor(
        &self,
        editor_id: String,
        editor: models::Editor,
        context: &Context,
    ) -> Box<Future<Item = UpdateEditorResponse, Error = ApiError> + Send> {
        let conn = self.db_pool.get().expect("db_pool error");
        let ret = match conn
            .transaction(|| {
                if Some(editor_id.clone()) != editor.editor_id {
                    return Err(
                        FatcatError::OtherBadRequest("editor_id doesn't match".to_string()).into(),
                    );
                }
                let auth_context = self.auth_confectionary.require_auth(
                    &conn,
                    &context.auth_data,
                    Some("update_editor"),
                )?;
                let editor_id = FatcatId::from_str(&editor_id)?;
                // DANGER! these permissions are for username updates only!
                if editor_id == auth_context.editor_id {
                    // self edit of username allowed
                    auth_context.require_role(FatcatRole::Editor)?;
                } else {
                    // admin can update any username
                    auth_context.require_role(FatcatRole::Admin)?;
                };
                update_editor_username(&conn, editor_id, editor.username).map(|e| e.into_model())
            })
            .map_err(|e| FatcatError::from(e))
        {
            Ok(editor) => UpdateEditorResponse::UpdatedEditor(editor),
            Err(fe) => generic_err_responses!(fe, UpdateEditorResponse),
        };
        Box::new(futures::done(Ok(ret)))
    }

    fn accept_editgroup(
        &self,
        editgroup_id: String,
        context: &Context,
    ) -> Box<Future<Item = AcceptEditgroupResponse, Error = ApiError> + Send> {
        let conn = self.db_pool.get().expect("db_pool error");
        let ret = match conn
            .transaction(|| {
                let editgroup_id = FatcatId::from_str(&editgroup_id)?;
                let auth_context = self.auth_confectionary.require_auth(
                    &conn,
                    &context.auth_data,
                    Some("accept_editgroup"),
                )?;
                auth_context.require_role(FatcatRole::Admin)?;
                // NOTE: this is currently redundant, but zero-cost
                auth_context.require_editgroup(&conn, editgroup_id)?;
                self.accept_editgroup_handler(&conn, editgroup_id)
            })
            .map_err(|e| FatcatError::from(e))
        {
            Ok(()) => {
                self.metrics.incr("editgroup.accepted").ok();
                AcceptEditgroupResponse::MergedSuccessfully(Success {
                    success: true,
                    message: "horray!".to_string(),
                })
            },
            Err(fe) => generic_auth_err_responses!(fe, AcceptEditgroupResponse),
        };
        Box::new(futures::done(Ok(ret)))
    }

    fn get_editgroup(
        &self,
        editgroup_id: String,
        _context: &Context,
    ) -> Box<Future<Item = GetEditgroupResponse, Error = ApiError> + Send> {
        let conn = self.db_pool.get().expect("db_pool error");
        let ret = match conn
            .transaction(|| {
                let editgroup_id = FatcatId::from_str(&editgroup_id)?;
                self.get_editgroup_handler(&conn, editgroup_id)
            })
            .map_err(|e| FatcatError::from(e))
        {
            Ok(entity) => GetEditgroupResponse::Found(entity),
            Err(fe) => generic_err_responses!(fe, GetEditgroupResponse),
        };
        Box::new(futures::done(Ok(ret)))
    }

    fn create_editgroup(
        &self,
        entity: models::Editgroup,
        context: &Context,
    ) -> Box<Future<Item = CreateEditgroupResponse, Error = ApiError> + Send> {
        let conn = self.db_pool.get().expect("db_pool error");
        let ret = match conn
            .transaction(|| {
                let auth_context = self.auth_confectionary.require_auth(
                    &conn,
                    &context.auth_data,
                    Some("create_editgroup"),
                )?;
                auth_context.require_role(FatcatRole::Editor)?;
                let mut entity = entity.clone();
                match entity.editor_id.clone() {
                    Some(editor_id) => {
                        if editor_id != auth_context.editor_id.to_string()
                            && !auth_context.has_role(FatcatRole::Admin)
                        {
                            bail!("not authorized to create editgroups in others' names");
                        }
                    }
                    None => {
                        entity.editor_id = Some(auth_context.editor_id.to_string());
                    }
                };
                self.create_editgroup_handler(&conn, entity)
            })
            .map_err(|e| FatcatError::from(e))
        {
            Ok(eg) => {
                self.metrics.incr("editgroup.created").ok();
                CreateEditgroupResponse::SuccessfullyCreated(eg)
            },
            Err(fe) => match fe {
                NotFound(_, _) => CreateEditgroupResponse::NotFound(fe.into()),
                DatabaseError(_) | InternalError(_) => {
                    error!("{}", fe);
                    capture_fail(&fe);
                    CreateEditgroupResponse::GenericError(fe.into())
                }
                _ => CreateEditgroupResponse::BadRequest(fe.into()),
            },
        };
        Box::new(futures::done(Ok(ret)))
    }

    fn get_changelog(
        &self,
        limit: Option<i64>,
        _context: &Context,
    ) -> Box<Future<Item = GetChangelogResponse, Error = ApiError> + Send> {
        let conn = self.db_pool.get().expect("db_pool error");
        // No transaction for GET
        let ret = match self
            .get_changelog_handler(&conn, limit)
            .map_err(|e| FatcatError::from(e))
        {
            Ok(changelog) => GetChangelogResponse::Success(changelog),
            Err(fe) => match fe {
                DatabaseError(_) | InternalError(_) => {
                    error!("{}", fe);
                    capture_fail(&fe);
                    GetChangelogResponse::GenericError(fe.into())
                }
                _ => GetChangelogResponse::BadRequest(fe.into()),
            },
        };
        Box::new(futures::done(Ok(ret)))
    }

    fn get_changelog_entry(
        &self,
        id: i64,
        _context: &Context,
    ) -> Box<Future<Item = GetChangelogEntryResponse, Error = ApiError> + Send> {
        let conn = self.db_pool.get().expect("db_pool error");
        // No transaction for GET
        let ret = match self
            .get_changelog_entry_handler(&conn, id)
            .map_err(|e| FatcatError::from(e))
        {
            Ok(entry) => GetChangelogEntryResponse::FoundChangelogEntry(entry),
            Err(fe) => generic_err_responses!(fe, GetChangelogEntryResponse),
        };
        Box::new(futures::done(Ok(ret)))
    }

    fn auth_oidc(
        &self,
        params: models::AuthOidc,
        context: &Context,
    ) -> Box<Future<Item = AuthOidcResponse, Error = ApiError> + Send> {
        let conn = self.db_pool.get().expect("db_pool error");
        let ret = match conn
            .transaction(|| {
                let auth_context = self.auth_confectionary.require_auth(
                    &conn,
                    &context.auth_data,
                    Some("auth_oidc"),
                )?;
                auth_context.require_role(FatcatRole::Superuser)?;
                let (editor, created) = self.auth_oidc_handler(&conn, params)?;
                // create an auth token with 31 day duration
                let token = self.auth_confectionary.create_token(
                    FatcatId::from_str(&editor.editor_id.clone().unwrap())?,
                    Some(chrono::Duration::days(31)),
                )?;
                let result = AuthOidcResult { editor, token };
                Ok((result, created))
            })
            .map_err(|e: Error| FatcatError::from(e))
        {
            Ok((result, true)) => {
                self.metrics.incr("account.signup").ok();
                AuthOidcResponse::Created(result)
            },
            Ok((result, false)) => {
                self.metrics.incr("account.login").ok();
                AuthOidcResponse::Found(result)
            },
            Err(fe) => match fe {
                DatabaseError(_) | InternalError(_) => {
                    error!("{}", fe);
                    capture_fail(&fe);
                    AuthOidcResponse::GenericError(fe.into())
                }
                _ => AuthOidcResponse::BadRequest(fe.into()),
            },
        };
        Box::new(futures::done(Ok(ret)))
    }

    fn auth_check(
        &self,
        role: Option<String>,
        context: &Context,
    ) -> Box<Future<Item = AuthCheckResponse, Error = ApiError> + Send> {
        let conn = self.db_pool.get().expect("db_pool error");
        let ret = match conn
            .transaction(|| {
                let auth_context = self.auth_confectionary.require_auth(
                    &conn,
                    &context.auth_data,
                    Some("auth_check"),
                )?;
                if let Some(role) = role {
                    let role = match role.to_lowercase().as_ref() {
                        "superuser" => FatcatRole::Superuser,
                        "admin" => FatcatRole::Admin,
                        "editor" => FatcatRole::Editor,
                        "bot" => FatcatRole::Bot,
                        "human" => FatcatRole::Human,
                        "public" => FatcatRole::Public,
                        _ => bail!("unknown auth role: {}", role),
                    };
                    auth_context.require_role(role)?;
                };
                Ok(())
            })
            .map_err(|e| FatcatError::from(e))
        {
            Ok(()) => AuthCheckResponse::Success(Success {
                success: true,
                message: "auth check successful!".to_string(),
            }),
            Err(fe) => match fe {
                DatabaseError(_) | InternalError(_) => {
                    error!("{}", fe);
                    capture_fail(&fe);
                    AuthCheckResponse::GenericError(fe.into())
                }
                _ => AuthCheckResponse::BadRequest(fe.into()),
            },
        };
        Box::new(futures::done(Ok(ret)))
    }
}