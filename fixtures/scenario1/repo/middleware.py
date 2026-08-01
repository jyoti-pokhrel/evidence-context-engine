from fastapi import Request
from typing import Callable


async def auth_middleware(request: Request, call_next: Callable):
    """Authentication middleware using JWT."""
    token = request.headers.get("Authorization")
    if not token:
        return None
    # JWT validation logic
    return await call_next(request)


async def logging_middleware(request: Request, call_next: Callable):
    """Logging middleware."""
    print(f"Request: {request.method} {request.url}")
    return await call_next(request)
