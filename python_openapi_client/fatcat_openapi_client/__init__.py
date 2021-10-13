# coding: utf-8

# flake8: noqa

"""
    fatcat

    Fatcat is a scalable, versioned, API-oriented catalog of bibliographic entities and file metadata.   # noqa: E501

    The version of the OpenAPI document: 0.4.0
    Contact: webservices@archive.org
    Generated by: https://openapi-generator.tech
"""


from __future__ import absolute_import

__version__ = "0.4.0"

# import apis into sdk package
from fatcat_openapi_client.api.default_api import DefaultApi

# import ApiClient
from fatcat_openapi_client.api_client import ApiClient
from fatcat_openapi_client.configuration import Configuration
from fatcat_openapi_client.exceptions import OpenApiException
from fatcat_openapi_client.exceptions import ApiTypeError
from fatcat_openapi_client.exceptions import ApiValueError
from fatcat_openapi_client.exceptions import ApiKeyError
from fatcat_openapi_client.exceptions import ApiException
# import models into sdk package
from fatcat_openapi_client.models.auth_oidc import AuthOidc
from fatcat_openapi_client.models.auth_oidc_result import AuthOidcResult
from fatcat_openapi_client.models.auth_token_result import AuthTokenResult
from fatcat_openapi_client.models.changelog_entry import ChangelogEntry
from fatcat_openapi_client.models.container_auto_batch import ContainerAutoBatch
from fatcat_openapi_client.models.container_entity import ContainerEntity
from fatcat_openapi_client.models.creator_auto_batch import CreatorAutoBatch
from fatcat_openapi_client.models.creator_entity import CreatorEntity
from fatcat_openapi_client.models.editgroup import Editgroup
from fatcat_openapi_client.models.editgroup_annotation import EditgroupAnnotation
from fatcat_openapi_client.models.editgroup_edits import EditgroupEdits
from fatcat_openapi_client.models.editor import Editor
from fatcat_openapi_client.models.entity_edit import EntityEdit
from fatcat_openapi_client.models.entity_history_entry import EntityHistoryEntry
from fatcat_openapi_client.models.error_response import ErrorResponse
from fatcat_openapi_client.models.file_auto_batch import FileAutoBatch
from fatcat_openapi_client.models.file_entity import FileEntity
from fatcat_openapi_client.models.file_url import FileUrl
from fatcat_openapi_client.models.fileset_auto_batch import FilesetAutoBatch
from fatcat_openapi_client.models.fileset_entity import FilesetEntity
from fatcat_openapi_client.models.fileset_file import FilesetFile
from fatcat_openapi_client.models.fileset_url import FilesetUrl
from fatcat_openapi_client.models.release_abstract import ReleaseAbstract
from fatcat_openapi_client.models.release_auto_batch import ReleaseAutoBatch
from fatcat_openapi_client.models.release_contrib import ReleaseContrib
from fatcat_openapi_client.models.release_entity import ReleaseEntity
from fatcat_openapi_client.models.release_ext_ids import ReleaseExtIds
from fatcat_openapi_client.models.release_ref import ReleaseRef
from fatcat_openapi_client.models.success import Success
from fatcat_openapi_client.models.webcapture_auto_batch import WebcaptureAutoBatch
from fatcat_openapi_client.models.webcapture_cdx_line import WebcaptureCdxLine
from fatcat_openapi_client.models.webcapture_entity import WebcaptureEntity
from fatcat_openapi_client.models.webcapture_url import WebcaptureUrl
from fatcat_openapi_client.models.work_auto_batch import WorkAutoBatch
from fatcat_openapi_client.models.work_entity import WorkEntity

