# -*- coding: utf-8 -*-

import uuid
from typing import Dict


def convert_ios_hierarchy(data: Dict, scale: int) -> Dict:

    def __travel(node):
        node['_id'] = str(uuid.uuid4())
        node['_type'] = node.pop('type', "null")
        if 'rect' in node:
            rect = node['rect']
            node['rect'] = {k: v * scale for k, v in rect.items()}
        for child in node.get('children', []):
            __travel(child)
        return node

    return __travel(data)