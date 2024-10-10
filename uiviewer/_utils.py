# -*- coding: utf-8 -*-

import base64
import json
from typing import Dict
from PIL import Image
from io import BytesIO

from uiviewer._logger import logger


def file2base64(path: str) -> str:
    with open(path, "rb") as file:
        base64_encoded = base64.b64encode(file.read())
        return base64_encoded.decode('utf-8')


def image2base64(image: Image.Image, format: str = "PNG") -> str:
    """
    PIL Image to base64 string
    """
    buffered = BytesIO()
    image.save(buffered, format=format)
    return base64.b64encode(buffered.getvalue()).decode('utf-8')


def str2json(s: str) -> Dict:
    try:
        json_obj = json.loads(s)
        return json_obj
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON data: {e}")
        return {}