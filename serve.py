#!/usr/bin/env python3

from __future__ import annotations

import argparse
import http.server
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parent


class SiteHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, directory: str | None = None, **kwargs):
        super().__init__(*args, directory=directory or str(ROOT), **kwargs)

    def do_GET(self) -> None:
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')
            return
        super().do_GET()

    def send_head(self):
        path = self.translate_path(self.path)
        if self.path != "/" and not Path(path).exists():
            self.path = "/index.html"
        return super().send_head()


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve the SWFI terminal site.")
    parser.add_argument("--host", default=os.environ.get("HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", "8344")))
    args = parser.parse_args()

    server = http.server.ThreadingHTTPServer((args.host, args.port), SiteHandler)
    print(f"serving {ROOT} on http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
