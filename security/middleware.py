"""
security/middleware.py — Convenience wrappers that combine all security modules.

This module provides helper functions that http_server.py and server.py
import to apply the full security stack without repeating boilerplate.

USAGE IN A HANDLER:
    from security.middleware import (
        check_rate_limit, check_body_size, send_security_headers,
        validate_script, check_path, get_cors_origin
    )

Each function returns a boolean or value and handles the HTTP error
response internally when the check fails, so the caller can simply:

    if not check_rate_limit(self):
        return  # 429 already sent

This keeps the handler code clean and the security logic centralized.
"""

from security import rate_limiter, headers, path_guard, input_validator, cors, logger


def check_rate_limit(handler, is_api=False):
    """
    Check rate limit for the client. Sends 429 if exceeded.

    Returns:
        True if the request is allowed, False if blocked (response already sent).
    """
    client_ip = handler.client_address[0]
    limit = rate_limiter.MAX_API_REQUESTS_PER_MINUTE if is_api else rate_limiter.MAX_REQUESTS_PER_MINUTE

    if rate_limiter.is_rate_limited(client_ip, limit):
        logger.log_block(client_ip, f"Rate limited (limit={limit}/min) on {handler.path}")
        handler.send_response(429)
        headers.add_security_headers(handler)
        handler.send_header('Retry-After', '60')
        handler.end_headers()
        handler.wfile.write(b'Too many requests')
        return False
    return True


def check_body_size(handler, content_length):
    """
    Check if request body is within size limits. Sends 413 if too large.

    Returns:
        True if acceptable, False if blocked (response already sent).
    """
    if input_validator.is_body_too_large(content_length):
        client_ip = handler.client_address[0]
        logger.log_block(client_ip, f"Oversized body ({content_length} bytes) on {handler.path}")
        handler.send_response(413)
        headers.add_security_headers(handler)
        handler.end_headers()
        handler.wfile.write(b'Request body too large')
        return False
    return True


def check_path(handler, request_path):
    """
    Check if a static file request is safe to serve. Sends 404 if blocked.

    Returns:
        True if safe, False if blocked (response already sent).
    """
    if not path_guard.is_safe_path(request_path, handler.translate_path):
        client_ip = handler.client_address[0]
        logger.log_block(client_ip, f"Blocked path: {request_path}")
        handler.send_response(404)
        headers.add_security_headers(handler)
        handler.end_headers()
        handler.wfile.write(b'Not found')
        return False
    return True


def validate_script(handler, script_name):
    """
    Validate a script name against the whitelist. Sends 400 if invalid.

    Returns:
        True if valid, False if blocked (response already sent).
    """
    if not input_validator.is_valid_script(script_name):
        client_ip = handler.client_address[0]
        logger.log_block(client_ip, f"Invalid script name: {script_name!r}")
        send_json_error(handler, 'Invalid script', 400)
        return False
    return True


def check_input_length(handler, text):
    """
    Check if script input text is within length limits. Sends 400 if too long.

    Returns:
        True if acceptable, False if blocked (response already sent).
    """
    if input_validator.is_input_too_long(text):
        client_ip = handler.client_address[0]
        logger.log_block(client_ip, f"Oversized script input ({len(text)} chars)")
        send_json_error(handler, 'Input too long', 400)
        return False
    return True


def send_security_headers(handler):
    """Add all security headers to the response. Call before end_headers()."""
    headers.add_security_headers(handler)


def get_cors_origin(handler, port):
    """Get the correct CORS origin for this request."""
    origin = handler.headers.get('Origin', '')
    return cors.get_allowed_origin(origin, port)


def send_json_error(handler, message, status_code=400):
    """Send a JSON error response with security headers and CORS."""
    import json
    handler.send_response(status_code)
    handler.send_header('Content-Type', 'application/json')
    headers.add_security_headers(handler)
    handler.end_headers()
    handler.wfile.write(json.dumps({
        'success': False,
        'error': message
    }).encode('utf-8'))
