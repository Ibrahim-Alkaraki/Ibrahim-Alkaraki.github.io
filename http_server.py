#!/usr/bin/env python3
"""
Combined HTTP + API server for the resume site.
Serves RESUME.html at /, static files, and script API endpoints.

All security logic lives in the security/ package:
  security/rate_limiter.py    — Per-IP request throttling
  security/headers.py         — CSP, X-Frame-Options, etc.
  security/path_guard.py      — Directory traversal protection
  security/input_validator.py — Script whitelist & body size limits
  security/cors.py            — Strict same-origin CORS
  security/logger.py          — Security event logging
  security/middleware.py      — Combines the above into simple checks
"""

import json
import subprocess
import threading
import queue
import sys
import os
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Import security modules
from security import path_guard, cors
from security.middleware import (
    check_rate_limit, check_body_size, check_path,
    validate_script, check_input_length, send_security_headers,
    get_cors_origin, send_json_error,
)
from security.input_validator import VALID_SCRIPTS
from security.logger import log_info, log_warn, log_block

PORT = 8000
SERVER_ROOT = os.path.dirname(os.path.abspath(__file__))

# Initialize security modules with server config
path_guard.configure(SERVER_ROOT)
cors.configure(PORT)


# --------------- Script process management ---------------

processes = {}


class ScriptProcess:
    def __init__(self, script_name):
        self.script_name = script_name
        self.process = None
        self.input_queue = queue.Queue()
        self.output_queue = queue.Queue()
        self.running = False

    def start(self):
        script_path = os.path.join(SERVER_ROOT, "scripts", f"{self.script_name}.py")
        # Resolve to absolute and verify it stays within scripts/
        script_path = os.path.realpath(script_path)
        scripts_dir = os.path.realpath(os.path.join(SERVER_ROOT, "scripts"))
        if not script_path.startswith(scripts_dir + os.sep):
            return False
        if not os.path.isfile(script_path):
            return False
        try:
            self.process = subprocess.Popen(
                [sys.executable, '-u', script_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                bufsize=0,
                cwd=scripts_dir,  # Restrict working directory to scripts/
            )
            self.running = True
            self._buffer = ""
            self._buffer_lock = threading.Lock()
            threading.Thread(target=self._read_output, daemon=True).start()
            threading.Thread(target=self._flush_buffer, daemon=True).start()
            threading.Thread(target=self._write_input, daemon=True).start()
            return True
        except Exception as e:
            print(f"Error starting {self.script_name}: {e}")
            return False

    def _read_output(self):
        try:
            while self.running and self.process:
                byte = self.process.stdout.read(1)
                if not byte:
                    with self._buffer_lock:
                        if self._buffer:
                            self.output_queue.put(self._buffer)
                            self._buffer = ""
                    break
                char = byte.decode('utf-8', errors='replace')
                if char == '\n':
                    with self._buffer_lock:
                        self.output_queue.put(self._buffer)
                        self._buffer = ""
                elif char == '\r':
                    continue
                else:
                    with self._buffer_lock:
                        self._buffer += char
        except Exception as e:
            print(f"Error reading output: {e}")
        finally:
            self.running = False

    def _flush_buffer(self):
        import time
        while self.running:
            time.sleep(0.1)
            with self._buffer_lock:
                if self._buffer:
                    self.output_queue.put(self._buffer)
                    self._buffer = ""

    def _write_input(self):
        try:
            while self.running:
                try:
                    data = self.input_queue.get(timeout=0.1)
                    if self.process and self.process.stdin:
                        self.process.stdin.write(data.encode('utf-8'))
                        self.process.stdin.flush()
                except queue.Empty:
                    continue
        except Exception as e:
            print(f"Error writing input: {e}")

    def send_input(self, data):
        self.input_queue.put(data)

    def get_output(self):
        output = []
        try:
            while True:
                line = self.output_queue.get(timeout=0.05)
                output.append(line)
        except queue.Empty:
            pass
        return output

    def stop(self):
        self.running = False
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=2)
            except:
                try:
                    self.process.kill()
                except:
                    pass


# --------------- Combined request handler ---------------


class ResumeHandler(SimpleHTTPRequestHandler):
    """Serves RESUME.html at / and handles /api/* for interactive scripts.
    All security logic delegated to the security/ package."""

    def do_GET(self):
        if not check_rate_limit(self):
            return

        if self.path == '/' or self.path == '':
            self.path = '/RESUME.html'
            return self._serve_safe_static()

        if self.path.startswith('/api/script-output'):
            return self._handle_script_output()

        if self.path == '/api/health':
            return self._send_json({'status': 'ok'})

        return self._serve_safe_static()

    def _serve_safe_static(self):
        if not check_path(self, self.path):
            return
        return super().do_GET()

    def end_headers(self):
        send_security_headers(self)
        super().end_headers()

    def do_POST(self):
        if not check_rate_limit(self, is_api=True):
            return

        content_length = int(self.headers.get('Content-Length', 0))
        if not check_body_size(self, content_length):
            return

        body = self.rfile.read(content_length).decode('utf-8')

        if self.path == '/api/start-script':
            return self._handle_start_script(body)
        elif self.path == '/api/script-input':
            return self._handle_script_input(body)
        elif self.path == '/api/stop-script':
            return self._handle_stop_script(body)

        self.send_error(404)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', get_cors_origin(self, PORT))
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    # ---- API handlers ----

    def _handle_start_script(self, body):
        try:
            data = json.loads(body)
            script = data.get('script')

            if not validate_script(self, script):
                return

            if script in processes:
                processes[script].stop()

            proc = ScriptProcess(script)
            if proc.start():
                processes[script] = proc
                log_info(self.client_address[0], f"Script started: {script}")
                self._send_json({'success': True})
            else:
                self._send_json({'success': False, 'error': 'Failed to start'}, 500)
        except (json.JSONDecodeError, TypeError, KeyError):
            log_warn(self.client_address[0], f"Malformed JSON on {self.path}")
            self._send_json({'success': False, 'error': 'Invalid request'}, 400)
        except Exception:
            self._send_json({'success': False, 'error': 'Internal error'}, 500)

    def _handle_script_input(self, body):
        try:
            data = json.loads(body)
            script = data.get('script')
            input_data = data.get('input', '')

            if not validate_script(self, script):
                return

            if script not in processes:
                return self._send_json({'success': False, 'error': 'Script not running'}, 400)

            if not check_input_length(self, input_data):
                return

            processes[script].send_input(input_data)
            self._send_json({'success': True})
        except (json.JSONDecodeError, TypeError, KeyError):
            log_warn(self.client_address[0], f"Malformed JSON on {self.path}")
            self._send_json({'success': False, 'error': 'Invalid request'}, 400)
        except Exception:
            self._send_json({'success': False, 'error': 'Internal error'}, 500)

    def _handle_script_output(self):
        try:
            query = urlparse(self.path).query
            params = parse_qs(query)
            script = params.get('script', [None])[0]

            if not validate_script(self, script):
                return

            if script not in processes:
                return self._send_json({'success': False, 'error': 'Script not running'}, 400)

            proc = processes[script]
            output = proc.get_output()

            self._send_json({
                'success': True,
                'output': output,
                'running': proc.running
            })
        except Exception:
            self._send_json({'success': False, 'error': 'Internal error'}, 500)

    def _handle_stop_script(self, body):
        try:
            data = json.loads(body)
            script = data.get('script')

            if not validate_script(self, script):
                return

            if script in processes:
                processes[script].stop()
                del processes[script]
                log_info(self.client_address[0], f"Script stopped: {script}")
                self._send_json({'success': True})
            else:
                self._send_json({'success': False, 'error': 'Script not running'}, 400)
        except (json.JSONDecodeError, TypeError, KeyError):
            log_warn(self.client_address[0], f"Malformed JSON on {self.path}")
            self._send_json({'success': False, 'error': 'Invalid request'}, 400)
        except Exception:
            self._send_json({'success': False, 'error': 'Internal error'}, 500)

    def _send_json(self, data, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', get_cors_origin(self, PORT))
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def log_message(self, format, *args):
        # Only log errors, skip routine request logs
        if args and len(args) >= 2 and str(args[1]).startswith('4'):
            super().log_message(format, *args)


if __name__ == '__main__':
    print(f"\nServing resume on http://localhost:{PORT}")
    print("Interactive script API included — no need to run server.py separately")
    print("Press Ctrl+C to stop\n")

    httpd = HTTPServer(("", PORT), ResumeHandler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        for proc in processes.values():
            proc.stop()
        httpd.shutdown()