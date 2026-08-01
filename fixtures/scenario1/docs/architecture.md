# Architecture Documentation

## System Overview

The Evidence Context Engine is a FastAPI application with the following components:

### Authentication

The system uses JWT tokens for authentication. The /login endpoint validates credentials and returns a JWT token.

### Middleware

The application uses a middleware chain:
1. Logging middleware
2. Authentication middleware (JWT validation)
3. Rate limiting middleware (to be implemented)

### API Structure

```
/login - Authentication endpoint
/api/* - Protected API endpoints
```

### Configuration

Application configuration is stored in config.py and includes rate limiting settings.

Last updated: 2026-01-12
