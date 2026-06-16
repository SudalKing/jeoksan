from typing import Any

from fastapi import status as http_status
from fastapi.responses import JSONResponse

def success(data: Any) -> JSONResponse:
    return JSONResponse(
        status_code=http_status.HTTP_200_OK,
        content={"status": "success", "data": data}
    )

def error(message: str) -> JSONResponse:
    return JSONResponse(
        status_code=http_status.HTTP_200_OK,
        content={"status": "error", "message": message}
    )
