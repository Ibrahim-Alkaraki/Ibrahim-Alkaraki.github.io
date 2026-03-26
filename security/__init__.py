"""
security/ — Centralized security modules for the Resume server.

This package contains all security logic used by http_server.py and server.py.
Each module handles one concern:

    rate_limiter.py   — Per-IP rate limiting to prevent brute force / DoS
    headers.py        — HTTP security headers (CSP, HSTS, X-Frame-Options, etc.)
    path_guard.py     — Path traversal protection & file access whitelist
    input_validator.py — Request body size limits & script name validation
    cors.py           — Strict same-origin CORS (no wildcard *)
    logger.py         — Security event logging (access denied, rate limits, errors)

Import the middleware helper to apply everything at once:

    from security.middleware import apply_security
"""
