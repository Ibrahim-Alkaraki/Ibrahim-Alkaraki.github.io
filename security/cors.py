"""
security/cors.py — Strict CORS (Cross-Origin Resource Sharing) policy.

WHY: The previous code used `Access-Control-Allow-Origin: *` which means
ANY website on the internet could make API calls to your server from a
visitor's browser. An attacker could:
  - Host a malicious page that calls /api/start-script on your server
  - Use a victim's browser as a proxy to interact with your scripts
  - Exfiltrate data from your API responses

HOW THIS MODULE FIXES IT:
  - Maintains a whitelist of allowed origins (your own server).
  - Only returns the requesting origin in the CORS header if it matches.
  - If the origin doesn't match, returns your primary origin (browser
    will block the cross-origin request).

CONFIGURING FOR PRODUCTION:
  - Call configure() at startup with your actual domain and port.
  - For DuckDNS deployment, add your public URL to the allowed set.
  - Example: configure(8000, extra_origins=['http://ibrahimakraki.duckdns.org:8000'])
"""

_allowed_origins = set()


def configure(port, extra_origins=None):
    """
    Set up the allowed origins list.

    Args:
        port: The port number the server runs on.
        extra_origins: Optional list of additional allowed origin strings
                      (e.g., your public DuckDNS URL).
    """
    global _allowed_origins
    _allowed_origins = {
        f'http://localhost:{port}',
        f'http://127.0.0.1:{port}',
    }
    if extra_origins:
        for origin in extra_origins:
            # Strip trailing slash for consistent matching
            _allowed_origins.add(origin.rstrip('/'))


def get_allowed_origin(request_origin, port):
    """
    Return the appropriate Access-Control-Allow-Origin value.

    Args:
        request_origin: The Origin header from the incoming request.
        port: Fallback port for the default origin.

    Returns:
        The origin string to send in the CORS header.
    """
    if request_origin in _allowed_origins:
        return request_origin
    # Default: return primary origin (browser will block mismatched origins)
    return f'http://localhost:{port}'
