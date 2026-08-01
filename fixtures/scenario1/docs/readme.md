# Evidence Context Engine

A fastAPI-based application for managing evidence context.

## Authentication

The application uses JWT tokens for authentication. Users must provide a valid JWT token in the Authorization header.

## API Endpoints

- POST /login - Authenticate user and get JWT token
- GET /api/data - Protected endpoint requiring authentication

## Setup

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Last updated: 2026-01-10
