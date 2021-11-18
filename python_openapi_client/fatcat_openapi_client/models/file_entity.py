# coding: utf-8

"""
    fatcat

    Fatcat is a scalable, versioned, API-oriented catalog of bibliographic entities and file metadata.   # noqa: E501

    The version of the OpenAPI document: 0.5.0
    Contact: webservices@archive.org
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six


class FileEntity(object):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'state': 'str',
        'ident': 'str',
        'revision': 'str',
        'redirect': 'str',
        'extra': 'dict(str, object)',
        'edit_extra': 'dict(str, object)',
        'size': 'int',
        'md5': 'str',
        'sha1': 'str',
        'sha256': 'str',
        'urls': 'list[FileUrl]',
        'mimetype': 'str',
        'content_scope': 'str',
        'release_ids': 'list[str]',
        'releases': 'list[ReleaseEntity]'
    }

    attribute_map = {
        'state': 'state',
        'ident': 'ident',
        'revision': 'revision',
        'redirect': 'redirect',
        'extra': 'extra',
        'edit_extra': 'edit_extra',
        'size': 'size',
        'md5': 'md5',
        'sha1': 'sha1',
        'sha256': 'sha256',
        'urls': 'urls',
        'mimetype': 'mimetype',
        'content_scope': 'content_scope',
        'release_ids': 'release_ids',
        'releases': 'releases'
    }

    def __init__(self, state=None, ident=None, revision=None, redirect=None, extra=None, edit_extra=None, size=None, md5=None, sha1=None, sha256=None, urls=None, mimetype=None, content_scope=None, release_ids=None, releases=None):  # noqa: E501
        """FileEntity - a model defined in OpenAPI"""  # noqa: E501

        self._state = None
        self._ident = None
        self._revision = None
        self._redirect = None
        self._extra = None
        self._edit_extra = None
        self._size = None
        self._md5 = None
        self._sha1 = None
        self._sha256 = None
        self._urls = None
        self._mimetype = None
        self._content_scope = None
        self._release_ids = None
        self._releases = None
        self.discriminator = None

        if state is not None:
            self.state = state
        if ident is not None:
            self.ident = ident
        if revision is not None:
            self.revision = revision
        if redirect is not None:
            self.redirect = redirect
        if extra is not None:
            self.extra = extra
        if edit_extra is not None:
            self.edit_extra = edit_extra
        if size is not None:
            self.size = size
        if md5 is not None:
            self.md5 = md5
        if sha1 is not None:
            self.sha1 = sha1
        if sha256 is not None:
            self.sha256 = sha256
        if urls is not None:
            self.urls = urls
        if mimetype is not None:
            self.mimetype = mimetype
        if content_scope is not None:
            self.content_scope = content_scope
        if release_ids is not None:
            self.release_ids = release_ids
        if releases is not None:
            self.releases = releases

    @property
    def state(self):
        """Gets the state of this FileEntity.  # noqa: E501


        :return: The state of this FileEntity.  # noqa: E501
        :rtype: str
        """
        return self._state

    @state.setter
    def state(self, state):
        """Sets the state of this FileEntity.


        :param state: The state of this FileEntity.  # noqa: E501
        :type: str
        """
        allowed_values = ["wip", "active", "redirect", "deleted"]  # noqa: E501
        if state not in allowed_values:
            raise ValueError(
                "Invalid value for `state` ({0}), must be one of {1}"  # noqa: E501
                .format(state, allowed_values)
            )

        self._state = state

    @property
    def ident(self):
        """Gets the ident of this FileEntity.  # noqa: E501

        base32-encoded unique identifier  # noqa: E501

        :return: The ident of this FileEntity.  # noqa: E501
        :rtype: str
        """
        return self._ident

    @ident.setter
    def ident(self, ident):
        """Sets the ident of this FileEntity.

        base32-encoded unique identifier  # noqa: E501

        :param ident: The ident of this FileEntity.  # noqa: E501
        :type: str
        """
        if ident is not None and len(ident) > 26:
            raise ValueError("Invalid value for `ident`, length must be less than or equal to `26`")  # noqa: E501
        if ident is not None and len(ident) < 26:
            raise ValueError("Invalid value for `ident`, length must be greater than or equal to `26`")  # noqa: E501
        if ident is not None and not re.search(r'[a-zA-Z2-7]{26}', ident):  # noqa: E501
            raise ValueError(r"Invalid value for `ident`, must be a follow pattern or equal to `/[a-zA-Z2-7]{26}/`")  # noqa: E501

        self._ident = ident

    @property
    def revision(self):
        """Gets the revision of this FileEntity.  # noqa: E501

        UUID (lower-case, dash-separated, hex-encoded 128-bit)  # noqa: E501

        :return: The revision of this FileEntity.  # noqa: E501
        :rtype: str
        """
        return self._revision

    @revision.setter
    def revision(self, revision):
        """Sets the revision of this FileEntity.

        UUID (lower-case, dash-separated, hex-encoded 128-bit)  # noqa: E501

        :param revision: The revision of this FileEntity.  # noqa: E501
        :type: str
        """
        if revision is not None and len(revision) > 36:
            raise ValueError("Invalid value for `revision`, length must be less than or equal to `36`")  # noqa: E501
        if revision is not None and len(revision) < 36:
            raise ValueError("Invalid value for `revision`, length must be greater than or equal to `36`")  # noqa: E501
        if revision is not None and not re.search(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', revision):  # noqa: E501
            raise ValueError(r"Invalid value for `revision`, must be a follow pattern or equal to `/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/`")  # noqa: E501

        self._revision = revision

    @property
    def redirect(self):
        """Gets the redirect of this FileEntity.  # noqa: E501

        base32-encoded unique identifier  # noqa: E501

        :return: The redirect of this FileEntity.  # noqa: E501
        :rtype: str
        """
        return self._redirect

    @redirect.setter
    def redirect(self, redirect):
        """Sets the redirect of this FileEntity.

        base32-encoded unique identifier  # noqa: E501

        :param redirect: The redirect of this FileEntity.  # noqa: E501
        :type: str
        """
        if redirect is not None and len(redirect) > 26:
            raise ValueError("Invalid value for `redirect`, length must be less than or equal to `26`")  # noqa: E501
        if redirect is not None and len(redirect) < 26:
            raise ValueError("Invalid value for `redirect`, length must be greater than or equal to `26`")  # noqa: E501
        if redirect is not None and not re.search(r'[a-zA-Z2-7]{26}', redirect):  # noqa: E501
            raise ValueError(r"Invalid value for `redirect`, must be a follow pattern or equal to `/[a-zA-Z2-7]{26}/`")  # noqa: E501

        self._redirect = redirect

    @property
    def extra(self):
        """Gets the extra of this FileEntity.  # noqa: E501

        Free-form JSON metadata that will be stored with the other entity metadata. See guide for (unenforced) schema conventions.   # noqa: E501

        :return: The extra of this FileEntity.  # noqa: E501
        :rtype: dict(str, object)
        """
        return self._extra

    @extra.setter
    def extra(self, extra):
        """Sets the extra of this FileEntity.

        Free-form JSON metadata that will be stored with the other entity metadata. See guide for (unenforced) schema conventions.   # noqa: E501

        :param extra: The extra of this FileEntity.  # noqa: E501
        :type: dict(str, object)
        """

        self._extra = extra

    @property
    def edit_extra(self):
        """Gets the edit_extra of this FileEntity.  # noqa: E501

        Free-form JSON metadata that will be stored with specific entity edits (eg, creation/update/delete).   # noqa: E501

        :return: The edit_extra of this FileEntity.  # noqa: E501
        :rtype: dict(str, object)
        """
        return self._edit_extra

    @edit_extra.setter
    def edit_extra(self, edit_extra):
        """Sets the edit_extra of this FileEntity.

        Free-form JSON metadata that will be stored with specific entity edits (eg, creation/update/delete).   # noqa: E501

        :param edit_extra: The edit_extra of this FileEntity.  # noqa: E501
        :type: dict(str, object)
        """

        self._edit_extra = edit_extra

    @property
    def size(self):
        """Gets the size of this FileEntity.  # noqa: E501

        Size of file in bytes. Non-zero.  # noqa: E501

        :return: The size of this FileEntity.  # noqa: E501
        :rtype: int
        """
        return self._size

    @size.setter
    def size(self, size):
        """Sets the size of this FileEntity.

        Size of file in bytes. Non-zero.  # noqa: E501

        :param size: The size of this FileEntity.  # noqa: E501
        :type: int
        """

        self._size = size

    @property
    def md5(self):
        """Gets the md5 of this FileEntity.  # noqa: E501

        MD5 hash of data, in hex encoding  # noqa: E501

        :return: The md5 of this FileEntity.  # noqa: E501
        :rtype: str
        """
        return self._md5

    @md5.setter
    def md5(self, md5):
        """Sets the md5 of this FileEntity.

        MD5 hash of data, in hex encoding  # noqa: E501

        :param md5: The md5 of this FileEntity.  # noqa: E501
        :type: str
        """
        if md5 is not None and len(md5) > 32:
            raise ValueError("Invalid value for `md5`, length must be less than or equal to `32`")  # noqa: E501
        if md5 is not None and len(md5) < 32:
            raise ValueError("Invalid value for `md5`, length must be greater than or equal to `32`")  # noqa: E501
        if md5 is not None and not re.search(r'[a-f0-9]{32}', md5):  # noqa: E501
            raise ValueError(r"Invalid value for `md5`, must be a follow pattern or equal to `/[a-f0-9]{32}/`")  # noqa: E501

        self._md5 = md5

    @property
    def sha1(self):
        """Gets the sha1 of this FileEntity.  # noqa: E501

        SHA-1 hash of data, in hex encoding  # noqa: E501

        :return: The sha1 of this FileEntity.  # noqa: E501
        :rtype: str
        """
        return self._sha1

    @sha1.setter
    def sha1(self, sha1):
        """Sets the sha1 of this FileEntity.

        SHA-1 hash of data, in hex encoding  # noqa: E501

        :param sha1: The sha1 of this FileEntity.  # noqa: E501
        :type: str
        """
        if sha1 is not None and len(sha1) > 40:
            raise ValueError("Invalid value for `sha1`, length must be less than or equal to `40`")  # noqa: E501
        if sha1 is not None and len(sha1) < 40:
            raise ValueError("Invalid value for `sha1`, length must be greater than or equal to `40`")  # noqa: E501
        if sha1 is not None and not re.search(r'[a-f0-9]{40}', sha1):  # noqa: E501
            raise ValueError(r"Invalid value for `sha1`, must be a follow pattern or equal to `/[a-f0-9]{40}/`")  # noqa: E501

        self._sha1 = sha1

    @property
    def sha256(self):
        """Gets the sha256 of this FileEntity.  # noqa: E501

        SHA-256 hash of data, in hex encoding  # noqa: E501

        :return: The sha256 of this FileEntity.  # noqa: E501
        :rtype: str
        """
        return self._sha256

    @sha256.setter
    def sha256(self, sha256):
        """Sets the sha256 of this FileEntity.

        SHA-256 hash of data, in hex encoding  # noqa: E501

        :param sha256: The sha256 of this FileEntity.  # noqa: E501
        :type: str
        """
        if sha256 is not None and len(sha256) > 64:
            raise ValueError("Invalid value for `sha256`, length must be less than or equal to `64`")  # noqa: E501
        if sha256 is not None and len(sha256) < 64:
            raise ValueError("Invalid value for `sha256`, length must be greater than or equal to `64`")  # noqa: E501
        if sha256 is not None and not re.search(r'[a-f0-9]{64}', sha256):  # noqa: E501
            raise ValueError(r"Invalid value for `sha256`, must be a follow pattern or equal to `/[a-f0-9]{64}/`")  # noqa: E501

        self._sha256 = sha256

    @property
    def urls(self):
        """Gets the urls of this FileEntity.  # noqa: E501


        :return: The urls of this FileEntity.  # noqa: E501
        :rtype: list[FileUrl]
        """
        return self._urls

    @urls.setter
    def urls(self, urls):
        """Sets the urls of this FileEntity.


        :param urls: The urls of this FileEntity.  # noqa: E501
        :type: list[FileUrl]
        """

        self._urls = urls

    @property
    def mimetype(self):
        """Gets the mimetype of this FileEntity.  # noqa: E501


        :return: The mimetype of this FileEntity.  # noqa: E501
        :rtype: str
        """
        return self._mimetype

    @mimetype.setter
    def mimetype(self, mimetype):
        """Sets the mimetype of this FileEntity.


        :param mimetype: The mimetype of this FileEntity.  # noqa: E501
        :type: str
        """

        self._mimetype = mimetype

    @property
    def content_scope(self):
        """Gets the content_scope of this FileEntity.  # noqa: E501


        :return: The content_scope of this FileEntity.  # noqa: E501
        :rtype: str
        """
        return self._content_scope

    @content_scope.setter
    def content_scope(self, content_scope):
        """Sets the content_scope of this FileEntity.


        :param content_scope: The content_scope of this FileEntity.  # noqa: E501
        :type: str
        """

        self._content_scope = content_scope

    @property
    def release_ids(self):
        """Gets the release_ids of this FileEntity.  # noqa: E501

        Set of identifier of release entities this file represents a full manifestation of. Usually a single release, but some files contain content of multiple full releases (eg, an issue of a journal).   # noqa: E501

        :return: The release_ids of this FileEntity.  # noqa: E501
        :rtype: list[str]
        """
        return self._release_ids

    @release_ids.setter
    def release_ids(self, release_ids):
        """Sets the release_ids of this FileEntity.

        Set of identifier of release entities this file represents a full manifestation of. Usually a single release, but some files contain content of multiple full releases (eg, an issue of a journal).   # noqa: E501

        :param release_ids: The release_ids of this FileEntity.  # noqa: E501
        :type: list[str]
        """

        self._release_ids = release_ids

    @property
    def releases(self):
        """Gets the releases of this FileEntity.  # noqa: E501

        Full release entities, included in GET responses when `releases` included in `expand` parameter. Ignored if included in PUT or POST requests.   # noqa: E501

        :return: The releases of this FileEntity.  # noqa: E501
        :rtype: list[ReleaseEntity]
        """
        return self._releases

    @releases.setter
    def releases(self, releases):
        """Sets the releases of this FileEntity.

        Full release entities, included in GET responses when `releases` included in `expand` parameter. Ignored if included in PUT or POST requests.   # noqa: E501

        :param releases: The releases of this FileEntity.  # noqa: E501
        :type: list[ReleaseEntity]
        """

        self._releases = releases

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.openapi_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, FileEntity):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
