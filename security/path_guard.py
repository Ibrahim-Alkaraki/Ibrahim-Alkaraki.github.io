"""
security/path_guard.py — Path traversal protection & file access whitelist.

WHY: Python's SimpleHTTPRequestHandler will serve ANY file in the working
directory tree by default. That means:
  - An attacker requesting /../../../etc/passwd could read system files
  - Requests to /server.py expose your source code
  - Requests to /deploy/setup_resume.sh expose deployment secrets
  - Requests to /.git/ expose your entire git history
  - Requests to /scripts/ expose backend script source code

HOW THIS MODULE WORKS:
  1. ALLOWED_FILES — an explicit whitelist of files that may be served
     (your public HTML pages). If the request matches one of these, it's
     allowed immediately.

  2. ALLOWED_EXTENSIONS — only files with these extensions can be served
     (for future CSS/JS/image assets you might add).

  3. BLOCKED_DIRECTORIES — even if the extension matches, these directories
     are always blocked: deploy/, docs/, scripts/, .git/, .env, __pycache__,
     security/. This protects source code, secrets, and config.

  4. Path resolution — the requested path is resolved to an absolute
     filesystem path using os.path.realpath(), then checked to ensure
     it stays under SERVER_ROOT. This defeats ../ traversal attacks.

ADDING NEW PUBLIC FILES:
  - Static assets (CSS, JS, images) in the root directory will be served
    if their extension is in ALLOWED_EXTENSIONS.
  - To serve a new HTML page, add it to ALLOWED_FILES.
  - NEVER add server-side scripts, config files, or deployment files
    to ALLOWED_FILES.
"""

import os
from urllib.parse import urlparse

# Set at import time; overridden by configure() if needed
SERVER_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- Whitelist: explicitly allowed file paths (relative to web root) ---
ALLOWED_FILES = {
    '/RESUME.html',
    '/fun_system_event.html',
}

# --- Whitelist: allowed file extensions for static assets ---
ALLOWED_EXTENSIONS = {
    '.html', '.css', '.js',
    '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico',
    '.woff', '.woff2', '.ttf', '.eot',
}

# --- Blacklist: directories that must NEVER be served, even if extension matches ---
BLOCKED_DIRECTORIES = (
    'deploy',
    'docs',
    'scripts',
    'security',
    '.git',
    '.env',
    '__pycache__',
)


def configure(server_root):
    """
    Set the server root directory. Call this once at startup.

    Args:
        server_root: Absolute path to the directory containing your site files.
    """
    global SERVER_ROOT
    SERVER_ROOT = os.path.realpath(server_root)


def is_safe_path(request_path, translate_path_fn):
    """
    Check if a request path is safe to serve.

    Args:
        request_path: The raw HTTP request path (e.g., '/RESUME.html', '/../etc/passwd').
        translate_path_fn: The handler's translate_path() method, which converts
                          URL paths to filesystem paths.

    Returns:
        True if the file is safe to serve, False if it should be blocked.
    """
    # Strip query strings
    clean = urlparse(request_path).path

    # Explicitly allowed files — fast path
    if clean in ALLOWED_FILES:
        return True

    # Check extension whitelist
    _, ext = os.path.splitext(clean)
    if ext.lower() not in ALLOWED_EXTENSIONS:
        return False

    # Resolve to absolute filesystem path
    fs_path = os.path.realpath(translate_path_fn(clean))
    server_root = os.path.realpath(SERVER_ROOT)

    # Must be under SERVER_ROOT (blocks ../ traversal)
    if not fs_path.startswith(server_root + os.sep) and fs_path != server_root:
        return False

    # Check against blocked directories
    rel = os.path.relpath(fs_path, server_root)
    for prefix in BLOCKED_DIRECTORIES:
        if rel == prefix or rel.startswith(prefix + os.sep):
            return False

    # Must be an actual file (not a directory listing)
    return os.path.isfile(fs_path)
