# -*- coding: utf-8 -*-

import os
import webbrowser
import uvicorn

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi import Request

from routers import api
from utils.models import ApiResponse


app = FastAPI()


current_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(current_dir, "static")

app.mount("/static", StaticFiles(directory=static_dir), name="static")

app.include_router(api.router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=ApiResponse(success=False, message=str(exc)).dict()
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ApiResponse(success=False, message=exc.detail).dict(),
    )


def open_browser():
    webbrowser.open_new("http://127.0.0.1:8000/static/index.html")


if __name__ == "__main__":
    import threading
    threading.Timer(1.0, open_browser).start()
    uvicorn.run(app, host="127.0.0.1", port=8000)