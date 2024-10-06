# -*- coding: utf-8 -*-

import base64
from PIL import Image
from io import BytesIO


def file_to_base64(path: str) -> str:
    with open(path, "rb") as file:
        base64_encoded = base64.b64encode(file.read())
        return base64_encoded.decode('utf-8')


def image_to_base64(image: Image.Image, format: str = "PNG") -> str:
    """
    PIL Image to base64 string
    """
    buffered = BytesIO()
    image.save(buffered, format=format)
    return base64.b64encode(buffered.getvalue()).decode('utf-8')
