# -*- coding: utf-8 -*-

import uuid
from uiviewer._models import BaseHierarchy


def convert_harmony_hierarchy(data: dict) -> BaseHierarchy:
    ret = {
        "jsonHierarchy": {
            "_id": "3e7bbe34-c6ed-4a06-abef-f44c3b852467",
            "children": []
        },
        "abilityName": "",
        "bundleName": "",
        "windowSize": [0, 0],
        "scale": 1
    }

    def __recursive_convert(node_a):
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
        }

        attributes = node_a.get("attributes", {})
        node_b["_type"] = attributes.get("type", "")
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
            node_b["children"] = [__recursive_convert(child) for child in children]

        return node_b

    # Recursively convert children of a to match b's structure
    ret["jsonHierarchy"]["children"] = [__recursive_convert(child) for child in data.get("children", [])]

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
    ret["activityName"] = first_child_attributes.get("abilityName", "")

    # Set bundleName based on the bundleName of the first attributes in the first children of a
    first_child_attributes = data.get("children", [{}])[0].get("attributes", {})
    ret["packageName"] = first_child_attributes.get("bundleName", "")

    return BaseHierarchy(**ret)