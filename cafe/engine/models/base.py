"""
Copyright 2013 Rackspace

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from xml.etree import ElementTree
from cafe.common.reporting import cclogging


class CommonToolsMixin(object):
    """Methods used to make building data models easier, common to all types"""
    @staticmethod
    def _bool_to_string(value, true_string='true', false_string='false'):
        """Returns a string representation of a boolean value, or the value
        provided if the value is not an instance of bool
        """
        if isinstance(value, bool):
            return true_string if value is True else false_string
        return value

    @staticmethod
    def _remove_empty_values(dictionary):
        """Returns a new dictionary based on 'dictionary', minus any keys with
        values that are None
        """
        return dict((k, v) for k, v in dictionary.iteritems() if v is not None)

    @staticmethod
    def _int_to_version_str(version_int):
        if isinstance(version_int, str):
            version_int = int(version_int)
        major = version_int // 1000000
        minor = (version_int - major * 1000000) // 1000
        patch = (version_int - major * 1000000 - minor * 1000)
        return '%s.%s.%s' % (str(major), str(minor), str(patch))


class JSON_ToolsMixin(object):
    """Methods used to make building json data models easier"""
    pass


class XML_ToolsMixin(object):
    """Methods used to make building xml data models easier"""
    @staticmethod
    def _set_xml_etree_element(
            xml_etree, property_dict, exclude_empty_properties=True):
        '''Sets a dictionary of keys and values as properties of the xml etree
        element if value is not None. Optionally, add all keys and values as
        properties if only if exclude_empty_properties == False.
        '''
        if exclude_empty_properties:
            property_dict = CommonToolsMixin._remove_empty_keys(property_dict)

        for key in property_dict:
            xml_etree.set(str(key), str(property_dict[key]))
        return xml_etree

    @staticmethod
    def _remove_xml_etree_namespace(doc, namespace):
        """Remove namespace in the passed document in place."""
        ns = u'{%s}' % namespace
        nsl = len(ns)
        for elem in doc.getiterator():
            for key in elem.attrib:
                if key.startswith(ns):
                    new_key = key[nsl:]
                    elem.attrib[new_key] = elem.attrib[key]
                    del elem.attrib[key]
            if elem.tag.startswith(ns):
                elem.tag = elem.tag[nsl:]
        return doc


class BAD_XML_TOOLS(object):
    '''THESE ARE BAD.  DON'T USE THEM.  They were created in a more innocent
    age, and are here for backwards compatability only.
    '''

    def _auto_value_to_dict(self, value):
        ret = None
        if isinstance(value, (int, str, unicode, bool)):
            ret = value
        elif isinstance(value, list):
            ret = []
            for item in value:
                ret.append(self._auto_value_to_dict(item))
        elif isinstance(value, dict):
            ret = {}
            for key in value.keys():
                ret[key] = self._auto_value_to_dict(value[key])
        elif isinstance(value, AutoMarshallingModel):
            ret = value._obj_to_json()
        return ret

    def _auto_to_dict(self):
        ret = {}
        for attr in vars(self).keys():
            value = vars(self).get(attr)
            if value is not None and attr != '_log':
                ret[attr] = self._auto_value_to_dict(value)

        if hasattr(self, 'ROOT_TAG'):
            return {self.ROOT_TAG: ret}
        else:
            return ret

    def _auto_to_xml(self):
        #XML is almost impossible to do without a schema definition because it
        #cannot be determined when an instance variable should be an attribute
        #of an element or text between that element's tags
        ret = ElementTree.Element(self.ROOT_TAG)
        for attr in vars(self).keys():
            value = vars(self).get(attr)
            if value is not None:
                assigned = self._auto_value_to_xml(attr, value)
                if isinstance(assigned, ElementTree.Element):
                    ret.append(assigned)
                else:
                    ret.set(attr, str(assigned))
        return ret


class BaseModel(object):
    __REPR_SEPARATOR__ = '\n'

    def __init__(self):
        self._log = cclogging.getLogger(
            cclogging.get_object_namespace(self.__class__))

    def __eq__(self, obj):
        try:
            if vars(obj) == vars(self):
                return True
        except:
            pass

        return False

    def __ne__(self, obj):
        if obj is None:
            return True

        if vars(obj) == vars(self):
            return False
        else:
            return True

    def __str__(self):
        strng = '<{0} object> {1}'.format(
            self.__class__.__name__, self.__REPR_SEPARATOR__)
        for key in self.__dict__.keys():
            if str(key) == '_log':
                continue
            strng = '{0}{1} = {2}{3}'.format(
                strng, str(key), str(self.__dict__[key]),
                self.__REPR_SEPARATOR__)
        return strng

    def __repr__(self):
        return self.__str__()


#Splitting the xml and json stuff into mixins cleans up the code but still
#muddies the AutoMarshallingModel namespace.  We could create
#tool objects in the AutoMarshallingModel, which would just act as
#sub-namespaces, to keep it clean. --Jose
class AutoMarshallingModel(
        BaseModel, CommonToolsMixin, JSON_ToolsMixin, XML_ToolsMixin,
        BAD_XML_TOOLS):
    """
    @summary: A class used as a base to build and contain the logic necessary
             to automatically create serialized requests and automatically
             deserialize responses in a format-agnostic way.
    """
    _log = cclogging.getLogger(__name__)

    def __init__(self):
        super(AutoMarshallingModel, self).__init__()
        self._log = cclogging.getLogger(
            cclogging.get_object_namespace(self.__class__))

    def serialize(self, format_type):
        serialization_exception = None
        try:
            serialize_method = '_obj_to_{0}'.format(format_type)
            return getattr(self, serialize_method)()
        except Exception as serialization_exception:
            pass

        if serialization_exception:
            try:
                self._log.error(
                    'Error occured during serialization of a data model into'
                    'the "{0}: \n{1}" format'.format(
                        format_type, serialization_exception))
                self._log.exception(serialization_exception)
            except Exception as exception:
                self._log.exception(exception)
                self._log.debug(
                    "Unable to log information regarding the "
                    "deserialization exception due to '{0}'".format(
                        serialization_exception))
        return None

    @classmethod
    def deserialize(cls, serialized_str, format_type):
        cls._log = cclogging.getLogger(
            cclogging.get_object_namespace(cls))

        model_object = None
        deserialization_exception = None
        if serialized_str and len(serialized_str) > 0:
            try:
                deserialize_method = '_{0}_to_obj'.format(format_type)
                model_object = getattr(cls, deserialize_method)(serialized_str)
            except Exception as deserialization_exception:
                cls._log.exception(deserialization_exception)

        #Try to log string and format_type if deserialization broke
        if deserialization_exception is not None:
            try:
                cls._log.debug(
                    "Deserialization Error: Attempted to deserialize type"
                    " using type: {0}".format(format_type.decode(
                        encoding='UTF-8', errors='ignore')))
                cls._log.debug(
                    "Deserialization Error: Unble to deserialize the "
                    "following:\n{0}".format(serialized_str.decode(
                        encoding='UTF-8', errors='ignore')))
            except Exception as exception:
                cls._log.exception(exception)
                cls._log.debug(
                    "Unable to log information regarding the "
                    "deserialization exception")

        return model_object

    #Serialization Functions
    def _obj_to_json(self):
        raise NotImplementedError

    def _obj_to_xml(self):
        raise NotImplementedError

    #Deserialization Functions
    @classmethod
    def _xml_to_obj(cls, serialized_str):
        raise NotImplementedError

    @classmethod
    def _json_to_obj(cls, serialized_str):
        raise NotImplementedError


class AutoMarshallingListModel(list, AutoMarshallingModel):
    """List-like AutoMarshallingModel used for some special cases"""
    def __str__(self):
        return list.__str__(self)
