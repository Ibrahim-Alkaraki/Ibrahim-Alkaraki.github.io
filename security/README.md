# security/ — Resume Server Security Package

This directory contains **all security logic** for the resume web server.
Each file handles one specific concern so the code stays organized and
auditable. Both `http_server.py` and `server.py` import from here.

---

## File Overview

| File                 | Purpose                                                |
|----------------------|--------------------------------------------------------|
| `__init__.py`        | Package marker + summary of what's inside              |
| `rate_limiter.py`    | Per-IP request throttling (sliding window)             |
| `headers.py`         | HTTP security response headers (CSP, XFO, etc.)       |
| `path_guard.py`      | Path traversal protection & file access whitelist      |
| `input_validator.py` | Request body size limits & script name whitelist       |
| `cors.py`            | Strict same-origin CORS policy                         |
| `logger.py`          | Security event logging (blocked requests, etc.)        |
| `middleware.py`      | Convenience wrappers combining all modules             |

---

## What Each Module Protects Against

### `rate_limiter.py` — Denial of Service & Brute Force
- **Threat:** An attacker floods the server with rapid requests to crash it
  or brute-force API endpoints.
- **Defense:** Tracks timestamps per client IP in a sliding 60-second window.
  Once the limit is hit, the server responds with HTTP 429 (Too Many Requests).
- **Config:** `MAX_REQUESTS_PER_MINUTE = 60` (pages), `MAX_API_REQUESTS_PER_MINUTE = 30` (API).

### `headers.py` — XSS, Clickjacking, MIME Sniffing
- **Threats:**
  - **XSS:** Injected scripts run in the user's browser.
  - **Clickjacking:** Page embedded in a malicious iframe; user clicks hidden buttons.
  - **MIME sniffing:** Browser misinterprets file type and executes it as script.
- **Defense:** Adds the following headers to every response:
  - `Content-Security-Policy` — restricts what resources the browser can load
  - `X-Frame-Options: DENY` — blocks iframe embedding
  - `X-Content-Type-Options: nosniff` — prevents MIME type guessing
  - `X-XSS-Protection: 1; mode=block` — legacy XSS filter
  - `Referrer-Policy` — limits URL leakage in Referer header
  - `Permissions-Policy` — disables camera, mic, geolocation APIs

### `path_guard.py` — Directory Traversal & Source Code Exposure
- **Threat:** An attacker requests `/../../../etc/passwd` or `/server.py` or
  `/.git/config` to read files they shouldn't have access to.
- **Defense:**
  1. Only files in `ALLOWED_FILES` (RESUME.html, fun_system_event.html) are served.
  2. Only files with `ALLOWED_EXTENSIONS` (.html, .css, .js, images, fonts) pass.
  3. `BLOCKED_DIRECTORIES` (deploy/, docs/, scripts/, security/, .git/) are always denied.
  4. `os.path.realpath()` resolves symlinks and `../` to prevent traversal.
  5. The resolved path must be under `SERVER_ROOT`.

### `input_validator.py` — Injection & Resource Exhaustion
- **Threats:**
  - **Command injection:** Crafted script names like `../../etc/passwd` could
    execute arbitrary files.
  - **DoS via large payloads:** Multi-GB request bodies exhaust memory.
  - **Stdin flooding:** Huge input strings piped to running scripts.
- **Defense:**
  - `VALID_SCRIPTS` frozenset — only 4 exact script names are allowed.
  - `MAX_REQUEST_BODY_BYTES = 4096` — POST bodies capped at 4 KB.
  - `MAX_SCRIPT_INPUT_LENGTH = 1024` — script stdin input capped at 1 KB.

### `cors.py` — Cross-Origin API Abuse
- **Threat:** A malicious website calls your API from a victim's browser,
  starting scripts or reading output on your server.
- **Defense:** Only requests from whitelisted origins (localhost, 127.0.0.1)
  get the correct `Access-Control-Allow-Origin` header. All others are
  rejected by the browser's CORS enforcement.
- **Production:** Call `cors.configure(port, extra_origins=['http://yourdomain:8000'])`
  to add your public URL.

### `logger.py` — Visibility & Incident Response
- **Threat:** Without logs, you can't detect or investigate attacks.
- **Defense:** Logs blocked requests, rate-limit hits, invalid script names,
  and script start/stop events to stderr (captured by systemd/journalctl).
- **Format:** `[timestamp] [SEVERITY] [client_ip] message`
- **Severity levels:** INFO, WARN, BLOCK.

### `middleware.py` — Centralized Enforcement
- **Purpose:** Wraps all the above modules into simple `check_*` functions
  that handlers call. Each function returns `True` (allowed) or `False`
  (blocked — the error response has already been sent).
- **Why centralize:** Prevents security checks from being accidentally
  skipped in individual handlers. One import, one function call.

---

## What Changed in the Servers

### `http_server.py` (main combined server)
| Before | After |
|--------|-------|
| `Access-Control-Allow-Origin: *` | Strict same-origin via `security/cors.py` |
| `SimpleHTTPRequestHandler` serves all files | `security/path_guard.py` blocks traversal |
| No security headers | Full CSP, XFO, etc. via `security/headers.py` |
| `str(e)` sent to client in errors | Generic "Internal error" message — no leaks |
| No rate limiting | Per-IP throttling via `security/rate_limiter.py` |
| No body size limits | 4 KB max via `security/input_validator.py` |
| Script names validated only on start | Validated on every endpoint (start/input/output/stop) |
| `subprocess.Popen` with no cwd restriction | `cwd=scripts_dir` — scripts run sandboxed |
| No logging | Security events logged via `security/logger.py` |

### `server.py` (standalone API server)
Same changes as above for all API endpoints.

### `RESUME.html` & `fun_system_event.html`
- Added `<meta http-equiv="Content-Security-Policy">` as defense-in-depth
  (works even if served by a non-hardened server).

### `deploy/setup_resume.sh`
| Before | After |
|--------|-------|
| No firewall | UFW configured: only ports 22 + 8000 open |
| DuckDNS token printed to screen | Token input hidden from output |
| Default file permissions | Restrictive: 700 dirs, 600 scripts, 755 HTML |

---

## How to Add a New Script

1. Place `your_script.py` in the `scripts/` directory.
2. Add `'your_script'` to the `VALID_SCRIPTS` frozenset in
   `security/input_validator.py`.
3. That's it — the middleware will validate it automatically.

## How to Add a New Public HTML Page

1. Place `your_page.html` in the project root.
2. Add `'/your_page.html'` to `ALLOWED_FILES` in `security/path_guard.py`.

## How to Allow Your Production Domain

In your server startup (e.g., `http_server.py`), after the `cors.configure()` call:

```python
cors.configure(PORT, extra_origins=[
    'http://ibrahimakraki.duckdns.org:8000',
])
```
