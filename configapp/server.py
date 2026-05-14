#!/usr/bin/env python3
"""
Simple HTTP server for HTAP Config Tool
Serves the web application on localhost:8000
"""

import http.server
import socketserver
import os
import sys

# Configuration
PORT = 8000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom request handler with CORS headers"""

    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

    def log_message(self, format, *args):
        """Custom log format"""
        print(f"[{self.log_date_time_string()}] {format % args}")


def main():
    """Start the HTTP server"""

    # Change to the application directory
    os.chdir(DIRECTORY)

    # Create server
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print("=" * 60)
        print("HTAP Run File Configuration Tool - Development Server")
        print("=" * 60)
        print(f"Serving directory: {DIRECTORY}")
        print(f"Server running at: http://localhost:{PORT}")
        print(f"Open in browser:   http://localhost:{PORT}/index.html")
        print("\nPress Ctrl+C to stop the server")
        print("=" * 60)

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\nServer stopped.")
            sys.exit(0)


if __name__ == "__main__":
    main()
