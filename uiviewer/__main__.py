# -*- coding: utf-8 -*-

import os
import webbrowser
import uvicorn
import threading
from typing import Union, Optional

from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, RedirectResponse

from uiviewer._device import (
    list_serials,
    init_device,
    cached_devices,
    AndroidDevice,
    IosDevice,
    HarmonyDevice
)
from uiviewer._models import ApiResponse


app = FastAPI()


current_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(current_dir, "static")

app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.exception_handler(Exception)
def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=ApiResponse(success=False, message=str(exc)).dict()
    )


@app.exception_handler(HTTPException)
def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ApiResponse(success=False, message=exc.detail).dict(),
    )


def open_browser(port):
    webbrowser.open_new(f"http://127.0.0.1:{port}")


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/health")
def health():
    return "ok"


@app.get("/{platform}/serials", response_model=ApiResponse)
def get_serials(platform: str):
    serials = list_serials(platform)
    return ApiResponse.doSuccess(serials)


@app.post("/{platform}/{serial}/connect", response_model=ApiResponse)
def connect(platform: str, serial: str, wdaUrl: Optional[str] = Query(None), maxDepth: Optional[int] = Query(None)):
    ret = init_device(platform, serial, wdaUrl, maxDepth)
    return ApiResponse.doSuccess(ret)


@app.get("/{platform}/{serial}/screenshot", response_model=ApiResponse)
def screenshot(platform: str, serial: str):
    device: Union[AndroidDevice, IosDevice, HarmonyDevice] = cached_devices.get((platform, serial))
    data = device.take_screenshot()
    return ApiResponse.doSuccess(data)


@app.get("/{platform}/{serial}/hierarchy", response_model=ApiResponse)
def dump_hierarchy(platform: str, serial: str):
    device: Union[AndroidDevice, IosDevice, HarmonyDevice] = cached_devices.get((platform, serial))
    data = device.dump_hierarchy()
    return ApiResponse.doSuccess(data)


def run(port=8000):
    timer = threading.Timer(1.0, open_browser, args=[port])
    timer.daemon = True
    timer.start()

    uvicorn.run(app, host="127.0.0.1", port=port)


if __name__ == "__main__":
    run()