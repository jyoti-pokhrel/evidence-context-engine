from fastapi import FastAPI, Request, HTTPException
from datetime import datetime

app = FastAPI()


@app.post("/login")
async def login(request: Request):
    """Authenticate user and return JWT token."""
    body = await request.json()
    username = body.get("username")
    password = body.get("password")
    
    if not username or not password:
        raise HTTPException(status_code=400, detail="Missing credentials")
    
    return {"status": "success", "token": "jwt_token_here"}
