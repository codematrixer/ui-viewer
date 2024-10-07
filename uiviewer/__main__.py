# -*- coding: utf-8 -*-

import os
import webbrowser
import uvicorn
import threading

from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from uiviewer.routers import api
from uiviewer._models import ApiResponse


app = FastAPI()


current_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(current_dir, "static")

app.mount("/static", StaticFiles(directory=static_dir), name="static")

app.include_router(api.router)


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


def run(port=8000):
    timer = threading.Timer(1.0, open_browser, args=[port])
    timer.daemon = True
    timer.start()

    uvicorn.run(app, host="127.0.0.1", port=port)


if __name__ == "__main__":
    run()