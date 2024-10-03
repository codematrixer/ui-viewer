# -*- coding: utf-8 -*-

from fastapi import APIRouter

from utils.device import list_serials, init_device, cached_devices
from utils.models import ApiResponse


router = APIRouter()


@router.get("/health")
async def health():
    return "ok"


@router.get("/{platform}/serials", response_model=ApiResponse)
async def get_serials(platform: str):
    serials = list_serials(platform)
    return ApiResponse.doSuccess(serials)


@router.post("/{platform}/{serial}/init", response_model=ApiResponse)
async def init(platform: str, serial: str):
    device = init_device(platform, serial)
    return ApiResponse.doSuccess(device)


@router.get("/{platform}/{serial}/screenshot", response_model=ApiResponse)
async def screenshot(platform: str, serial: str):
    device = cached_devices.get((platform, serial))
    data = device.take_screenshot()
    return ApiResponse.doSuccess(data)


@router.get("/{platform}/{serial}/hierarchy", response_model=ApiResponse)
async def dump_hierarchy(platform: str, serial: str):
    device = cached_devices.get((platform, serial))
    data = device.dump_hierarchy()
    return ApiResponse.doSuccess(data)
