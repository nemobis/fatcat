# coding: utf-8

"""
    fatcat

    Fatcat is a scalable, versioned, API-oriented catalog of bibliographic entities and file metadata.   # noqa: E501

    The version of the OpenAPI document: 0.4.0
    Contact: webservices@archive.org
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six


class ContainerEntity(object):
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
        'name': 'str',
        'container_type': 'str',
        'publication_status': 'str',
        'publisher': 'str',
        'issnl': 'str',
        'issne': 'str',
        'issnp': 'str',
        'wikidata_qid': 'str'
    }

    attribute_map = {
        'state': 'state',
        'ident': 'ident',
        'revision': 'revision',
        'redirect': 'redirect',
        'extra': 'extra',
        'edit_extra': 'edit_extra',
        'name': 'name',
        'container_type': 'container_type',
        'publication_status': 'publication_status',
        'publisher': 'publisher',
        'issnl': 'issnl',
        'issne': 'issne',
        'issnp': 'issnp',
        'wikidata_qid': 'wikidata_qid'
    }

    def __init__(self, state=None, ident=None, revision=None, redirect=None, extra=None, edit_extra=None, name=None, container_type=None, publication_status=None, publisher=None, issnl=None, issne=None, issnp=None, wikidata_qid=None):  # noqa: E501
        """ContainerEntity - a model defined in OpenAPI"""  # noqa: E501

        self._state = None
        self._ident = None
        self._revision = None
        self._redirect = None
        self._extra = None
        self._edit_extra = None
        self._name = None
        self._container_type = None
        self._publication_status = None
        self._publisher = None
        self._issnl = None
        self._issne = None
        self._issnp = None
        self._wikidata_qid = None
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
        if name is not None:
            self.name = name
        if container_type is not None:
            self.container_type = container_type
        if publication_status is not None:
            self.publication_status = publication_status
        if publisher is not None:
            self.publisher = publisher
        if issnl is not None:
            self.issnl = issnl
        if issne is not None:
            self.issne = issne
        if issnp is not None:
            self.issnp = issnp
        if wikidata_qid is not None:
            self.wikidata_qid = wikidata_qid

    @property
    def state(self):
        """Gets the state of this ContainerEntity.  # noqa: E501


        :return: The state of this ContainerEntity.  # noqa: E501
        :rtype: str
        """
        return self._state

    @state.setter
    def state(self, state):
        """Sets the state of this ContainerEntity.


        :param state: The state of this ContainerEntity.  # noqa: E501
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
        """Gets the ident of this ContainerEntity.  # noqa: E501

        base32-encoded unique identifier  # noqa: E501

        :return: The ident of this ContainerEntity.  # noqa: E501
        :rtype: str
        """
        return self._ident

    @ident.setter
    def ident(self, ident):
        """Sets the ident of this ContainerEntity.

        base32-encoded unique identifier  # noqa: E501

        :param ident: The ident of this ContainerEntity.  # noqa: E501
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
        """Gets the revision of this ContainerEntity.  # noqa: E501

        UUID (lower-case, dash-separated, hex-encoded 128-bit)  # noqa: E501

        :return: The revision of this ContainerEntity.  # noqa: E501
        :rtype: str
        """
        return self._revision

    @revision.setter
    def revision(self, revision):
        """Sets the revision of this ContainerEntity.

        UUID (lower-case, dash-separated, hex-encoded 128-bit)  # noqa: E501

        :param revision: The revision of this ContainerEntity.  # noqa: E501
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
        """Gets the redirect of this ContainerEntity.  # noqa: E501

        base32-encoded unique identifier  # noqa: E501

        :return: The redirect of this ContainerEntity.  # noqa: E501
        :rtype: str
        """
        return self._redirect

    @redirect.setter
    def redirect(self, redirect):
        """Sets the redirect of this ContainerEntity.

        base32-encoded unique identifier  # noqa: E501

        :param redirect: The redirect of this ContainerEntity.  # noqa: E501
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
        """Gets the extra of this ContainerEntity.  # noqa: E501

        Free-form JSON metadata that will be stored with the other entity metadata. See guide for (unenforced) schema conventions.   # noqa: E501

        :return: The extra of this ContainerEntity.  # noqa: E501
        :rtype: dict(str, object)
        """
        return self._extra

    @extra.setter
    def extra(self, extra):
        """Sets the extra of this ContainerEntity.

        Free-form JSON metadata that will be stored with the other entity metadata. See guide for (unenforced) schema conventions.   # noqa: E501

        :param extra: The extra of this ContainerEntity.  # noqa: E501
        :type: dict(str, object)
        """

        self._extra = extra

    @property
    def edit_extra(self):
        """Gets the edit_extra of this ContainerEntity.  # noqa: E501

        Free-form JSON metadata that will be stored with specific entity edits (eg, creation/update/delete).   # noqa: E501

        :return: The edit_extra of this ContainerEntity.  # noqa: E501
        :rtype: dict(str, object)
        """
        return self._edit_extra

    @edit_extra.setter
    def edit_extra(self, edit_extra):
        """Sets the edit_extra of this ContainerEntity.

        Free-form JSON metadata that will be stored with specific entity edits (eg, creation/update/delete).   # noqa: E501

        :param edit_extra: The edit_extra of this ContainerEntity.  # noqa: E501
        :type: dict(str, object)
        """

        self._edit_extra = edit_extra

    @property
    def name(self):
        """Gets the name of this ContainerEntity.  # noqa: E501

        Name of the container (eg, Journal title). Required for entity creation.  # noqa: E501

        :return: The name of this ContainerEntity.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this ContainerEntity.

        Name of the container (eg, Journal title). Required for entity creation.  # noqa: E501

        :param name: The name of this ContainerEntity.  # noqa: E501
        :type: str
        """

        self._name = name

    @property
    def container_type(self):
        """Gets the container_type of this ContainerEntity.  # noqa: E501

        Type of container, eg 'journal' or 'proceedings'. See Guide for list of valid types.  # noqa: E501

        :return: The container_type of this ContainerEntity.  # noqa: E501
        :rtype: str
        """
        return self._container_type

    @container_type.setter
    def container_type(self, container_type):
        """Sets the container_type of this ContainerEntity.

        Type of container, eg 'journal' or 'proceedings'. See Guide for list of valid types.  # noqa: E501

        :param container_type: The container_type of this ContainerEntity.  # noqa: E501
        :type: str
        """

        self._container_type = container_type

    @property
    def publication_status(self):
        """Gets the publication_status of this ContainerEntity.  # noqa: E501

        Whether the container is active, discontinued, etc  # noqa: E501

        :return: The publication_status of this ContainerEntity.  # noqa: E501
        :rtype: str
        """
        return self._publication_status

    @publication_status.setter
    def publication_status(self, publication_status):
        """Sets the publication_status of this ContainerEntity.

        Whether the container is active, discontinued, etc  # noqa: E501

        :param publication_status: The publication_status of this ContainerEntity.  # noqa: E501
        :type: str
        """

        self._publication_status = publication_status

    @property
    def publisher(self):
        """Gets the publisher of this ContainerEntity.  # noqa: E501

        Name of the organization or entity responsible for publication. Not the complete imprint/brand.   # noqa: E501

        :return: The publisher of this ContainerEntity.  # noqa: E501
        :rtype: str
        """
        return self._publisher

    @publisher.setter
    def publisher(self, publisher):
        """Sets the publisher of this ContainerEntity.

        Name of the organization or entity responsible for publication. Not the complete imprint/brand.   # noqa: E501

        :param publisher: The publisher of this ContainerEntity.  # noqa: E501
        :type: str
        """

        self._publisher = publisher

    @property
    def issnl(self):
        """Gets the issnl of this ContainerEntity.  # noqa: E501

        Linking ISSN number (ISSN-L). Should be valid and registered with issn.org  # noqa: E501

        :return: The issnl of this ContainerEntity.  # noqa: E501
        :rtype: str
        """
        return self._issnl

    @issnl.setter
    def issnl(self, issnl):
        """Sets the issnl of this ContainerEntity.

        Linking ISSN number (ISSN-L). Should be valid and registered with issn.org  # noqa: E501

        :param issnl: The issnl of this ContainerEntity.  # noqa: E501
        :type: str
        """
        if issnl is not None and len(issnl) > 9:
            raise ValueError("Invalid value for `issnl`, length must be less than or equal to `9`")  # noqa: E501
        if issnl is not None and len(issnl) < 9:
            raise ValueError("Invalid value for `issnl`, length must be greater than or equal to `9`")  # noqa: E501
        if issnl is not None and not re.search(r'\d{4}-\d{3}[0-9X]', issnl):  # noqa: E501
            raise ValueError(r"Invalid value for `issnl`, must be a follow pattern or equal to `/\d{4}-\d{3}[0-9X]/`")  # noqa: E501

        self._issnl = issnl

    @property
    def issne(self):
        """Gets the issne of this ContainerEntity.  # noqa: E501

        Electronic ISSN number (ISSN-E). Should be valid and registered with issn.org  # noqa: E501

        :return: The issne of this ContainerEntity.  # noqa: E501
        :rtype: str
        """
        return self._issne

    @issne.setter
    def issne(self, issne):
        """Sets the issne of this ContainerEntity.

        Electronic ISSN number (ISSN-E). Should be valid and registered with issn.org  # noqa: E501

        :param issne: The issne of this ContainerEntity.  # noqa: E501
        :type: str
        """
        if issne is not None and len(issne) > 9:
            raise ValueError("Invalid value for `issne`, length must be less than or equal to `9`")  # noqa: E501
        if issne is not None and len(issne) < 9:
            raise ValueError("Invalid value for `issne`, length must be greater than or equal to `9`")  # noqa: E501
        if issne is not None and not re.search(r'\d{4}-\d{3}[0-9X]', issne):  # noqa: E501
            raise ValueError(r"Invalid value for `issne`, must be a follow pattern or equal to `/\d{4}-\d{3}[0-9X]/`")  # noqa: E501

        self._issne = issne

    @property
    def issnp(self):
        """Gets the issnp of this ContainerEntity.  # noqa: E501

        Print ISSN number (ISSN-P). Should be valid and registered with issn.org  # noqa: E501

        :return: The issnp of this ContainerEntity.  # noqa: E501
        :rtype: str
        """
        return self._issnp

    @issnp.setter
    def issnp(self, issnp):
        """Sets the issnp of this ContainerEntity.

        Print ISSN number (ISSN-P). Should be valid and registered with issn.org  # noqa: E501

        :param issnp: The issnp of this ContainerEntity.  # noqa: E501
        :type: str
        """
        if issnp is not None and len(issnp) > 9:
            raise ValueError("Invalid value for `issnp`, length must be less than or equal to `9`")  # noqa: E501
        if issnp is not None and len(issnp) < 9:
            raise ValueError("Invalid value for `issnp`, length must be greater than or equal to `9`")  # noqa: E501
        if issnp is not None and not re.search(r'\d{4}-\d{3}[0-9X]', issnp):  # noqa: E501
            raise ValueError(r"Invalid value for `issnp`, must be a follow pattern or equal to `/\d{4}-\d{3}[0-9X]/`")  # noqa: E501

        self._issnp = issnp

    @property
    def wikidata_qid(self):
        """Gets the wikidata_qid of this ContainerEntity.  # noqa: E501


        :return: The wikidata_qid of this ContainerEntity.  # noqa: E501
        :rtype: str
        """
        return self._wikidata_qid

    @wikidata_qid.setter
    def wikidata_qid(self, wikidata_qid):
        """Sets the wikidata_qid of this ContainerEntity.


        :param wikidata_qid: The wikidata_qid of this ContainerEntity.  # noqa: E501
        :type: str
        """

        self._wikidata_qid = wikidata_qid

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
        if not isinstance(other, ContainerEntity):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
