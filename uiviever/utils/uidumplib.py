# coding: utf-8

import re
import xml.dom.minidom
import uuid

from utils.models import HarmonyHierarchy


def parse_bounds(text):
    m = re.match(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]', text)
    if m is None:
        return None
    (lx, ly, rx, ry) = map(int, m.groups())
    return dict(x=lx, y=ly, width=rx - lx, height=ry - ly)


def safe_xmlstr(s):
    return s.replace("$", "-")


def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")


def str2int(v):
    return int(v)


def convstr(v):
    return v


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


def _parse_uiautomator_node(node):
    ks = {}
    for key, value in node.attributes.items():
        key = __alias.get(key, key)
        f = __parsers.get(key)
        if value is None:
            ks[key] = None
        elif f:
            ks[key] = f(value)
    if 'bounds' in ks:
        lx, ly, rx, ry = map(int, ks.pop('bounds'))
        ks['rect'] = dict(x=lx, y=ly, width=rx - lx, height=ry - ly)
    return ks


def get_android_hierarchy(d):
    page_xml = d.dump_hierarchy(compressed=False, pretty=False).encode('utf-8')
    return android_hierarchy_to_json(page_xml)


def android_hierarchy_to_json(page_xml: bytes):
    """
    Returns:
        JSON object
    """
    dom = xml.dom.minidom.parseString(page_xml)
    root = dom.documentElement

    def travel(node):
        """ return current node info """
        if node.attributes is None:
            return
        json_node = _parse_uiautomator_node(node)
        json_node['_id'] = str(uuid.uuid4())
        if node.childNodes:
            children = []
            for n in node.childNodes:
                child = travel(n)
                if child:
                    # child["_parent"] = json_node["_id"]
                    children.append(child)
            json_node['children'] = children
        return json_node

    return travel(root)


def get_ios_hierarchy(d, scale, md=None):
    if md != '' or md is not None:
        d.appium_settings({"snapshotMaxDepth": md})
    sourcejson = d.source(format='json')

    def travel(node):
        node['_id'] = str(uuid.uuid4())
        node['_type'] = node.pop('type', "null")
        if node.get('rect'):
            rect = node['rect']
            nrect = {}
            for k, v in rect.items():
                nrect[k] = v * scale
            node['rect'] = nrect

        for child in node.get('children', []):
            travel(child)
        return node

    return travel(sourcejson)


def get_webview_hierarchy(d):
    pass


def convert_harmony_hierarchy(data: dict) -> HarmonyHierarchy:
    ret = {
        "xmlHierarchy": None,
        "jsonHierarchy": {
            "_id": "3e7bbe34-c6ed-4a06-abef-f44c3b852467",
            "children": []
        },
        "abilityName": "",
        "bundleName": "",
        "windowSize": [0, 0],
        "scale": 1
    }

    def recursive_convert(node_a):
        node_b = {
            "index": 0,
            "text": "",
            "id": "",
            "type": "",
            "description": "",
            "checkable": False,
            "clickable": False,
            "enabled": False,
            "focusable": False,
            "focused": False,
            "scrollable": False,
            "longClickable": False,
            "password": False,
            "selected": False,
            "rect": {
                "x": 0,
                "y": 0,
                "width": 0,
                "height": 0
            },
            "_id": str(uuid.uuid4()),
        }

        attributes = node_a.get("attributes", {})
        node_b["type"] = attributes.get("type", "")
        node_b["id"] = attributes.get("id", "")
        node_b["description"] = attributes.get("description", "")
        node_b["text"] = attributes.get("text", "")
        node_b["checkable"] = attributes.get("checkable", "").lower() == "true"
        node_b["clickable"] = attributes.get("clickable", "").lower() == "true"
        node_b["enabled"] = attributes.get("enabled", "").lower() == "true"
        node_b["focusable"] = attributes.get("focused", "").lower() == "true"
        node_b["focused"] = attributes.get("focused", "").lower() == "true"
        node_b["scrollable"] = attributes.get("scrollable", "").lower() == "true"
        node_b["longClickable"] = attributes.get("longClickable", "").lower() == "true"
        bounds = attributes.get("bounds", "")
        bounds = bounds.strip("[]").split("][")
        node_b["rect"]["x"] = int(bounds[0].split(",")[0])
        node_b["rect"]["y"] = int(bounds[0].split(",")[1])
        node_b["rect"]["width"] = int(bounds[1].split(",")[0]) - int(bounds[0].split(",")[0])
        node_b["rect"]["height"] = int(bounds[1].split(",")[1]) - int(bounds[0].split(",")[1])

        # TODO Remove unnecessary attributes

        children = node_a.get("children", [])
        if children:
            node_b["children"] = [recursive_convert(child) for child in children]

        return node_b

    # Recursively convert children of a to match b's structure
    ret["jsonHierarchy"]["children"] = [recursive_convert(child) for child in data.get("children", [])]

    # Set windowSize based on the bounds of the first attributes in a
    first_bounds = data["attributes"].get("bounds", "")
    if first_bounds:
        first_bounds = first_bounds.strip("[]").split("][")
        ret["windowSize"] = [
            int(first_bounds[1].split(",")[0]) - int(first_bounds[0].split(",")[0]),
            int(first_bounds[1].split(",")[1]) - int(first_bounds[0].split(",")[1])
        ]

    # Set abilityName based on the abilityName of the first attributes in the first children of a
    first_child_attributes = data.get("children", [{}])[0].get("attributes", {})
    ret["abilityName"] = first_child_attributes.get("abilityName", "")

    # Set bundleName based on the bundleName of the first attributes in the first children of a
    first_child_attributes = data.get("children", [{}])[0].get("attributes", {})
    ret["bundleName"] = first_child_attributes.get("bundleName", "")
    print(ret)
    return HarmonyHierarchy(**ret)