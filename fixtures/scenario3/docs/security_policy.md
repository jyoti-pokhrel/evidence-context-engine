# Security Policy

## Rate Limiting Requirements

All authentication endpoints must implement rate limiting to prevent brute force attacks.

**Requirements:**
- Maximum 5 failed login attempts per minute per IP
- Lock account after 10 failed attempts
- Log all rate limit violations

## Authentication Security

JWT tokens must:
- Expire after 1 hour
- Use RS256 algorithm
- Include user ID and role in claims

## Compliance

This policy is restricted to security team members only.

Last updated: 2026-01-09
