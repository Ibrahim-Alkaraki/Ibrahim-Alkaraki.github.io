"""
security/headers.py — HTTP security response headers.

WHY EACH HEADER MATTERS:

  X-Content-Type-Options: nosniff
    Prevents the browser from "guessing" a file's content type.
    Without this, an attacker could upload a .txt file containing JavaScript
    and the browser might execute it as script.

  X-Frame-Options: DENY
    Blocks the page from being embedded in an <iframe> on another site.
    Prevents clickjacking attacks where an attacker overlays invisible
    frames to trick users into clicking hidden buttons.

  X-XSS-Protection: 1; mode=block
    Legacy header for older browsers. Tells the browser to block the page
    if a reflected XSS attack is detected in the URL/parameters.

  Referrer-Policy: strict-origin-when-cross-origin
    Controls how much URL information is sent in the Referer header.
    'strict-origin-when-cross-origin' sends the full path for same-origin
    requests but only the origin (domain) for cross-origin requests,
    preventing internal URL paths from leaking to external sites.

  Permissions-Policy: camera=(), microphone=(), geolocation=()
    Explicitly disables browser features this site doesn't need.
    Even if XSS is achieved, the attacker can't access these APIs.

  Content-Security-Policy (CSP):
    The most important header. Controls exactly what the browser is
    allowed to load and execute:
      - default-src 'self'        → Only load resources from same origin
      - script-src 'self' 'unsafe-inline' → Allow our inline scripts
        (NOTE: 'unsafe-inline' is needed because RESUME.html has inline
        <script> blocks. Ideally these would move to external .js files
        and this could be tightened to just 'self' + a nonce.)
      - style-src 'self' 'unsafe-inline'  → Allow our inline styles
      - img-src 'self' data:      → Allow images from same origin + data URIs
      - connect-src 'self'        → Fetch/XHR only to same origin
      - frame-ancestors 'none'    → No one can iframe this page
      - form-action 'self'        → Forms can only submit to same origin
      - base-uri 'self'           → Prevents <base> tag hijacking
"""


def add_security_headers(handler):
    """
    Add all security headers to an HTTP response.

    Args:
        handler: An http.server.BaseHTTPRequestHandler instance.
                 Must be called BEFORE handler.end_headers().
    """
    handler.send_header('X-Content-Type-Options', 'nosniff')
    handler.send_header('X-Frame-Options', 'DENY')
    handler.send_header('X-XSS-Protection', '1; mode=block')
    handler.send_header('Referrer-Policy', 'strict-origin-when-cross-origin')
    handler.send_header('Permissions-Policy', 'camera=(), microphone=(), geolocation=()')
    handler.send_header(
        'Content-Security-Policy',
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "font-src 'self'; "
        "connect-src 'self'; "
        "frame-ancestors 'none'; "
        "form-action 'self'; "
        "base-uri 'self'"
    )
