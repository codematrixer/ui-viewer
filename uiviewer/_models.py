# -*- coding: utf-8 -*-

import enum

from pydantic import BaseModel
from typing import Any, Union, Dict, Tuple, Optional


class Platform(str, enum.Enum):
    ANDROID = "android"
    IOS = "ios"
    HARMONY = "harmony"


class ApiResponse(BaseModel):
    success: bool = True
    data: Any = None
    message: Union[str] = None

    @classmethod
    def doSuccess(cls, data):
        return ApiResponse(success=True, data=data, message=None)

    @classmethod
    def doError(cls, message):
        return ApiResponse(success=False, data=None, message=message)


class BaseHierarchy(BaseModel):
    jsonHierarchy: Optional[Dict] = None
    windowSize: Tuple[int, int]
    scale: int = 1
    activityName: Optional[str] = None
    packageName: Optional[str] = None


class XPathLiteRequest(BaseModel):
    tree_data: Dict[str, Any]
    node_id: str