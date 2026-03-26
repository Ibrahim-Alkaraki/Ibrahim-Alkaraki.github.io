"""
security/rate_limiter.py — Per-IP rate limiting.

WHY: Without rate limiting, an attacker can:
  - Brute-force API endpoints (start thousands of script processes)
  - DoS the server with rapid requests
  - Scrape all content at machine speed

HOW IT WORKS:
  - Tracks request timestamps per client IP in a sliding 60-second window.
  - If a client exceeds the configured threshold, further requests get HTTP 429.
  - Two tiers: general requests (page loads) and API requests (tighter limit).
  - Thread-safe — uses a lock since the HTTP server is multi-threaded.

TUNING:
  - MAX_REQUESTS_PER_MINUTE: for static page loads (generous — 60/min default)
  - MAX_API_REQUESTS_PER_MINUTE: for /api/* endpoints (tighter — 30/min default)
  - Adjust these based on expected legitimate traffic patterns.
"""

import time
import threading
from collections import defaultdict

# ----- Configuration -----
MAX_REQUESTS_PER_MINUTE = 60
MAX_API_REQUESTS_PER_MINUTE = 30

# ----- Internal state -----
_rate_limits = defaultdict(list)  # {ip: [timestamp, timestamp, ...]}
_rate_lock = threading.Lock()


def is_rate_limited(client_ip, limit=MAX_REQUESTS_PER_MINUTE):
    """
    Check if client_ip has exceeded the rate limit.

    Args:
        client_ip: The IP address string of the client.
        limit: Max allowed requests in a 60-second window.

    Returns:
        True if the client should be blocked (over limit), False if allowed.
    """
    now = time.time()
    with _rate_lock:
        timestamps = _rate_limits[client_ip]
        # Remove entries older than 60 seconds (sliding window)
        _rate_limits[client_ip] = [t for t in timestamps if now - t < 60]
        if len(_rate_limits[client_ip]) >= limit:
            return True
        _rate_limits[client_ip].append(now)
        return False
