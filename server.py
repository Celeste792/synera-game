#!/usr/bin/env python
"""Simple HTTP server with gzip support for .wasm files."""
import http.server
import os
import sys

PORT = 8000
DIR = sys.argv[1] if len(sys.argv) > 1 else '.'

class GzipHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIR, **kwargs)

    def end_headers(self):
        # Enable CORS for local testing
        self.send_header('Cross-Origin-Opener-Policy', 'same-origin')
        self.send_header('Cross-Origin-Embedder-Policy', 'require-corp')
        super().end_headers()

    def translate_path(self, path):
        path = super().translate_path(path)
        return path

    def send_head(self):
        path = self.translate_path(self.path)
        gz_path = path + '.gz'

        # Serve pre-compressed .wasm.gz if it exists
        if os.path.exists(gz_path) and path.endswith('.wasm'):
            f = open(gz_path, 'rb')
            fs = os.fstat(f.fileno())
            self.send_response(200)
            self.send_header('Content-Type', 'application/wasm')
            self.send_header('Content-Encoding', 'gzip')
            self.send_header('Content-Length', str(fs.st_size))
            self.send_header('Cache-Control', 'public, max-age=86400')
            self.end_headers()
            return f

        return super().send_head()

print(f"Serving {os.path.abspath(DIR)} on http://0.0.0.0:{PORT}")
print("Supports .wasm.gz pre-compressed files")
http.server.HTTPServer(('0.0.0.0', PORT), GzipHandler).serve_forever()
