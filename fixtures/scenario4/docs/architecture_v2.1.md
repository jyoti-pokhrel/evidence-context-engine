# Architecture Documentation v2.1

## System Overview

The Evidence Context Engine is a FastAPI application.

### Authentication

The system uses OAuth2 for authentication. The /login endpoint validates credentials using OAuth2 flow and returns an access token.

### Middleware

The application uses logging and authentication middleware.

Last updated: 2026-01-10
