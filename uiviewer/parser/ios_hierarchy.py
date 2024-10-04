# -*- coding: utf-8 -*-

import uuid


def get_ios_hierarchy(client, scale, md=None):
    if md:
        client.appium_settings({"snapshotMaxDepth": md})
    sourcejson = client.source(format='json')

    def __travel(node):
        node['_id'] = str(uuid.uuid4())
        node['_type'] = node.pop('type', "null")
        if 'rect' in node:
            rect = node['rect']
            node['rect'] = {k: v * scale for k, v in rect.items()}
        for child in node.get('children', []):
            __travel(child)
        return node

    return __travel(sourcejson)