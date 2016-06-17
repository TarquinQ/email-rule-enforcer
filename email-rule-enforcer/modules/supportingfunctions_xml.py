import xml.etree.ElementTree as ET
from .supportingfunctions import convert_text_to_boolean, force_text_to_boolean


def set_value_if_xmlnode_exists(configdict, key, Node, xpath):
    """Set a config value only if the value is in the xml"""
    node_found = Node.find(xpath)
    if node_found is not None and isinstance(node_found, ET.Element):
        configdict[key] = node_found.text


def get_value_if_xmlnode_exists(Node, xpath):
    """Return a config value only if the xml subnode exists"""
    node_found = Node.find(xpath)
    if node_found is not None and isinstance(node_found, ET.Element):
        return node_found.text
    else:
        return None


def get_attributes_if_xmlnode_exists(Node, xpath):
    """Return a set of attributes only if the xml subnode exists"""
    node_found = Node.find(xpath)
    if node_found is not None and isinstance(node_found, ET.Element):
        return node_found.attrib
    else:
        return None


def get_attribvalue_if_exists_in_xmlNode(Node, attrib_to_get):
    """Returns an attributes' value only if the value is in the attrib dict"""
    if attrib_to_get in Node.attrib:
        return Node.attrib[attrib_to_get]
    else:
        return None


def set_boolean_if_xmlnode_exists(configdict, key, Node, xpath):
    """Set a config value only if the value is in the xml"""
    node_found = Node.find(xpath)
    if node_found is not None and isinstance(node_found, ET.Element):
        node_val = force_text_to_boolean(node_found.text)
        if node_val is not None:
            configdict[key] = node_val


def xpath_findall(Node, xpath):
    """Performs XPath findall search, handling errors"""
    try:
        for subnode in Node.findall(xpath):
            yield subnode
    except TypeError:
        return []
