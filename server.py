"""Local web server for the FirmwareFix MVP. Standard library only."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
from firmwarefix.analyzer import analyze

ROOT = Path(__file__).resolve().parent
MAX_BODY = 1_000_000

class FirmwareFixHandler(BaseHTTPRequestHandler):
    def _json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path not in ("/", "/index.html"):
            self.send_error(404, "Not found")
            return
        body = (ROOT / "index.html").read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.path != "/api/analyze":
            self._json(404, {"error": "Endpoint not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._json(400, {"error": "Invalid Content-Length"})
            return
        if length <= 0 or length > MAX_BODY:
            self._json(400, {"error": "Request body must be between 1 byte and 1 MB"})
            return
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._json(400, {"error": "Request body must be valid UTF-8 JSON"})
            return
        if not isinstance(payload, dict):
            self._json(400, {"error": "JSON body must be an object"})
            return
        values = [payload.get(key, "") for key in ("source", "diagnostics", "logs")]
        if not all(isinstance(value, str) for value in values):
            self._json(400, {"error": "source, diagnostics and logs must be strings"})
            return
        source, diagnostics, logs = values
        findings = [item.to_dict() for item in analyze(source, diagnostics, logs)]
        self._json(200, {"ok": True, "findings": findings, "summary": {
            "finding_count": len(findings), "source_chars": len(source),
            "diagnostic_chars": len(diagnostics), "log_chars": len(logs)}})

    def log_message(self, fmt, *args):
        print(f"[FirmwareFix] {self.address_string()} - {fmt % args}")

if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 8000), FirmwareFixHandler)
    print("FirmwareFix running at http://127.0.0.1:8000")
    print("Press Ctrl+C to stop. Local-only server; do not expose publicly as-is.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down FirmwareFix.")
    finally:
        server.server_close()
