"""
security/input_validator.py — Request validation & script name whitelist.

WHY:
  - Without body size limits, an attacker can send a multi-GB POST body
    and exhaust server memory (DoS).
  - Without script name validation on EVERY endpoint, an attacker could
    pass a crafted name like "../../etc/passwd" to execute arbitrary files.
  - Without input length limits, a malicious user could pipe huge strings
    into a running script's stdin.

HOW:
  - VALID_SCRIPTS: hard-coded whitelist of script names that can be run.
    These map to files in scripts/ (e.g., 'file_manager_enhanced' →
    scripts/file_manager_enhanced.py). No path components allowed.
  - MAX_REQUEST_BODY_BYTES: upper bound on POST body size (4 KB).
  - MAX_SCRIPT_INPUT_LENGTH: upper bound on text piped to a script (1 KB).

ADDING A NEW SCRIPT:
  - Place the .py file in scripts/
  - Add the name (without .py) to VALID_SCRIPTS below
  - The script will be sandboxed with cwd=scripts/ when started
"""

# ----- Configuration -----

MAX_REQUEST_BODY_BYTES = 4096       # 4 KB — plenty for JSON commands
MAX_SCRIPT_INPUT_LENGTH = 1024      # 1 KB — plenty for menu choices / text input

# Hard-coded whitelist — ONLY these scripts can be started via the API.
# Names must be simple identifiers (no slashes, no dots, no path traversal).
VALID_SCRIPTS = frozenset([
    'password_manager_enhanced',
    'network_device_manager_enhanced',
    'file_manager_enhanced',
    'log_parsing_analysis',
])


def is_valid_script(name):
    """
    Check if 'name' is an allowed script.

    Args:
        name: The script name string from the request body.

    Returns:
        True if valid, False otherwise.
    """
    if not isinstance(name, str):
        return False
    return name in VALID_SCRIPTS


def is_body_too_large(content_length):
    """
    Check if the request body exceeds the size limit.

    Args:
        content_length: Integer from the Content-Length header.

    Returns:
        True if the body is too large, False if acceptable.
    """
    return content_length > MAX_REQUEST_BODY_BYTES


def is_input_too_long(text):
    """
    Check if script input text exceeds the length limit.

    Args:
        text: The input string to be piped to a script.

    Returns:
        True if too long, False if acceptable.
    """
    return len(text) > MAX_SCRIPT_INPUT_LENGTH
