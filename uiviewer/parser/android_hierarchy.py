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


def get_android_hierarchy(page_xml: bytes) -> Dict:
    dom = xml.dom.minidom.parseString(page_xml)
    root = dom.documentElement

    def travel(node):
        if node.attributes is None:
            return
        json_node = _parse_uiautomator_node(node)
        json_node['_id'] = str(uuid.uuid4())
        if node.childNodes:
            children = [travel(n) for n in node.childNodes if travel(n)]
            json_node['children'] = children
        return json_node

    return travel(root)