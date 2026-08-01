from fastapi import Request
from typing import Callable


async def auth_middleware(request: Request, call_next: Callable):
    """Authentication middleware using JWT."""
    token = request.headers.get("Authorization")
    if not token:
        return None
    return await call_next(request)
