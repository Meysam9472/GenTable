import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


logger = logging.getLogger(__name__)


# 1. Handle unexpected Python exceptions (500)
async def global_exception_handler(
    request: Request,
    exc: Exception
):
    logger.error(
        f"Unhandled API error: {request.method} {request.url.path}",
        exc_info=(type(exc), exc, exc.__traceback__)
    )

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error"
        }
    )


# 2. Handle HTTP exceptions (404, 401, 403, etc.)
async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException
):
    logger.warning(
        f"HTTP error {exc.status_code}: "
        f"{request.method} {request.url.path} - {exc.detail}"
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail
        },
        headers=exc.headers
    )


# 3. Handle request validation errors (422)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    logger.warning(
        f"Validation error: {request.method} "
        f"{request.url.path} - {exc.errors()}"
    )

    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "Invalid request data",
            "errors": exc.errors()
        }
    )
