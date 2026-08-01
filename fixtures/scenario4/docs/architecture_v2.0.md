# Architecture Documentation v2.0

## System Overview

The Evidence Context Engine is a FastAPI application.

### Authentication

The system uses JWT tokens for authentication. The /login endpoint validates credentials and returns a JWT token.

### Middleware

The application uses logging and authentication middleware.

Last updated: 2025-12-15
