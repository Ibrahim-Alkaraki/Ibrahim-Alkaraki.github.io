"""
security/logger.py — Security event logging.

WHY: Without logging, you have no visibility into:
  - Who is trying to access blocked paths (directory traversal attempts)
  - Which IPs are being rate-limited (possible DoS or brute force)
  - Failed API requests (possible fuzzing or exploitation attempts)
  - When scripts are started/stopped (audit trail)

It's impossible to respond to an incident you can't see.

HOW:
  - Logs to stderr (captured by systemd/journalctl in production).
  - Each log line includes: timestamp, severity, client IP, and event detail.
  - Severity levels: INFO (normal operations), WARN (suspicious but not
    necessarily malicious), BLOCK (request was denied by security controls).
  - In production, pipe these logs to a centralized logging system.

EVENTS LOGGED:
  - BLOCK: rate-limited request
  - BLOCK: path traversal / forbidden file access attempt
  - BLOCK: invalid script name submitted
  - BLOCK: oversized request body
  - WARN:  malformed JSON in API request
  - INFO:  script started / stopped
"""

import sys
import time

# Set to False to disable logging (e.g., during tests)
ENABLED = True


def _log(severity, client_ip, message):
    """Write a structured log line to stderr."""
    if not ENABLED:
        return
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    print(f"[{timestamp}] [{severity}] [{client_ip}] {message}", file=sys.stderr)


def log_info(client_ip, message):
    """Log a normal operational event."""
    _log("INFO", client_ip, message)


def log_warn(client_ip, message):
    """Log a suspicious but non-critical event."""
    _log("WARN", client_ip, message)


def log_block(client_ip, message):
    """Log a request that was denied by security controls."""
    _log("BLOCK", client_ip, message)
