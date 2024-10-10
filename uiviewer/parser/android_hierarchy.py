# -*- coding: utf-8 -*-

import xml.dom.minidom
import uuid
from typing import Dict

from uiviewer.parser.utils import parse_bounds, safe_xmlstr, str2bool, str2int, convstr

__alias = {
    'class': '_type',
    'resource-id': 'resourceId',
    'content-desc': 'description',
    'long-clickable': 'longClickable',
    'bounds': 'rect',
}

__parsers = {
    '_type': safe_xmlstr,  # node className
    # Android
    'rect': parse_bounds,
    'text': convstr,
    'resourceId': convstr,
    'package': convstr,
    'checkable': str2bool,
    'scrollable': str2bool,
    'focused': str2bool,
    'clickable': str2bool,
    'selected': str2bool,
    'longClickable': str2bool,
    'focusable': str2bool,
    'password': str2bool,
    'index': int,
    'description': convstr,
    # iOS
    'name': convstr,
    'label': convstr,
    'x': str2int,
    'y': str2int,
    'width': str2int,
    'height': str2int,
    # iOS && Android
    'enabled': str2bool,
}


def _parse_node_attributes(node):
    attributes = {}
    for key, value in node.attributes.items():
        key = __alias.get(key, key)
        parser = __parsers.get(key)
        if value is None:
            attributes[key] = None
        elif parser:
            attributes[key] = parser(value)
    return attributes


def _parse_uiautomator_node(node):
    attributes = _parse_node_attributes(node)
    if 'bounds' in attributes:
        lx, ly, rx, ry = map(int, attributes.pop('bounds'))
        attributes['rect'] = dict(x=lx, y=ly, width=rx - lx, height=ry - ly)
    return attributes


def convert_android_hierarchy(page_xml: str) -> Dict:
    dom = xml.dom.minidom.parseString(page_xml)
    root = dom.documentElement

    def __travel(node, parent_id=""):
        if node.attributes is None:
            return
        json_node = _parse_uiautomator_node(node)
        json_node['_id'] = str(uuid.uuid4())
        json_node['_parentId'] = parent_id
        json_node['xpath'] = ""
        json_node.pop("package", None)
        if node.childNodes:
            children = []
            for n in node.childNodes:
                child = __travel(n, json_node['_id'])
                if child:
                    children.append(child)
            json_node['children'] = children

        # Sort the keys
        keys_order = ['xpath', '_type', 'resourceId', 'text', 'description']
        sorted_node = {k: json_node[k] for k in keys_order if k in json_node}
        sorted_node.update({k: json_node[k] for k in json_node if k not in keys_order})

        return sorted_node

    return __travel(root)