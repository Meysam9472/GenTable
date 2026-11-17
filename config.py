from fastapi import FastAPI
from apps.time_table_maker import time_table
from apps.users import users
from throttling import limiter
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from core.logging_config import setup_logging
from core.exception_handlers import (
    global_exception_handler,
    http_exception_handler,
    validation_exception_handler
)
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

setup_logging()

app = FastAPI()

# Register the limiter to the app state
app.state.limiter = limiter

# Add the exception handler for rate limits
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add middleware if you want global rate limits later(Activates above limiter object
# parameter: default_limits=["10/minute"])
app.add_middleware(SlowAPIMiddleware)

app.include_router(time_table.router, tags=["time_table"])
app.include_router(users.router, tags=["users"])

app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)