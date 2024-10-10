# -*- coding: utf-8 -*-

import uuid
from typing import Dict


def convert_harmony_hierarchy(data: Dict) -> Dict:
    ret = {"_id": str(uuid.uuid4()), "children": [], "_parentId": ""}

    def __travel(node_a, parent_id=""):
        node_b = {
            "index": 0,
            "text": "",
            "id": "",
            "_type": "",
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
            "_parentId": parent_id,
            "xpath": ""
        }

        attributes = node_a.get("attributes", {})
        node_b["xpath"] = attributes.get("xpath", "")
        node_b["_type"] = attributes.get("type", "")
        node_b["id"] = attributes.get("id", "")
        node_b["description"] = attributes.get("description", "")
        node_b["text"] = attributes.get("text", "")
        node_b["checkable"] = attributes.get("checkable", "").lower() == "true"
        node_b["clickable"] = attributes.get("clickable", "").lower() == "true"
        node_b["enabled"] = attributes.get("enabled", "").lower() == "true"
        node_b["focusable"] = attributes.get("focusable", "").lower() == "true"
        node_b["focused"] = attributes.get("focused", "").lower() == "true"
        node_b["scrollable"] = attributes.get("scrollable", "").lower() == "true"
        node_b["longClickable"] = attributes.get("longClickable", "").lower() == "true"
        bounds = attributes.get("bounds", "")
        bounds = bounds.strip("[]").split("][")
        node_b["rect"]["x"] = int(bounds[0].split(",")[0])
        node_b["rect"]["y"] = int(bounds[0].split(",")[1])
        node_b["rect"]["width"] = int(bounds[1].split(",")[0]) - int(bounds[0].split(",")[0])
        node_b["rect"]["height"] = int(bounds[1].split(",")[1]) - int(bounds[0].split(",")[1])

        children = node_a.get("children", [])
        if children:
            node_b["children"] = [__travel(child, node_b["_id"]) for child in children]

        return node_b

    # Recursively convert children of a to match b's structure
    ret["children"] = [__travel(child, ret["_id"]) for child in data.get("children", [])]

    return ret