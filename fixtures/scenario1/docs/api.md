# API Documentation

## Authentication

### POST /login

Authenticates a user and returns a JWT token.

**Request:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "status": "success",
  "token": "jwt_token"
}
```

**Status Codes:**
- 200: Success
- 400: Missing credentials
- 401: Invalid credentials

## Rate Limiting

Rate limiting is configured in config.py but not yet implemented. The configuration specifies:
- 60 requests per minute
- Burst limit of 10 requests

Last updated: 2026-01-11
