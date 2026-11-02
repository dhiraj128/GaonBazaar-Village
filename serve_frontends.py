import http.server
import socketserver
import threading
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SERVERS = [
    {
        "name": "Customer App",
        "port": 3000,
        "dir": os.path.join(BASE_DIR, "apps", "customer", "build", "web")
    },
    {
        "name": "Vendor App",
        "port": 3001,
        "dir": os.path.join(BASE_DIR, "apps", "vendor", "build", "web")
    },
    {
        "name": "Runner App",
        "port": 3002,
        "dir": os.path.join(BASE_DIR, "apps", "runner", "build", "web")
    },
    {
        "name": "Super Admin",
        "port": 3003,
        "dir": os.path.join(BASE_DIR, "apps", "admin", "dist")
    }
]

class SPAHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Enable CORS and caching headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache')
        super().end_headers()

    def do_GET(self):
        # Strip subpath prefix if present from GitHub Pages base href
        for prefix in ['/GaonBazaar-Village/customer', '/GaonBazaar-Village/vendor', '/GaonBazaar-Village/runner', '/GaonBazaar-Village/admin']:
            if self.path.startswith(prefix):
                self.path = self.path[len(prefix):] or '/'
                break
        # Serve index.html for SPA routes if file doesn't exist
        path = self.translate_path(self.path)
        if not os.path.exists(path) and not '.' in os.path.basename(self.path):
            self.path = '/index.html'
        return super().do_GET()

def make_handler(directory):
    return lambda *args, **kwargs: SPAHandler(*args, directory=directory, **kwargs)

def start_server(config):
    port = config["port"]
    directory = config["dir"]
    name = config["name"]
    
    if not os.path.exists(directory):
        print(f"Directory not found for {name}: {directory}")
        return

    handler = make_handler(directory)
    # Allow address reuse
    socketserver.TCPServer.allow_reuse_address = True
    try:
        with socketserver.TCPServer(("", port), handler) as httpd:
            print(f"[{name}] Serving at http://localhost:{port}")
            httpd.serve_forever()
    except Exception as e:
        print(f"[{name}] Port {port} error: {e}")

if __name__ == "__main__":
    threads = []
    print("=" * 60)
    print("Starting GaonBazaar Frontends on Dedicated Local Ports...")
    print("=" * 60)
    for s in SERVERS:
        t = threading.Thread(target=start_server, args=(s,), daemon=True)
        t.start()
        threads.append(t)
    
    # Keep main thread alive
    for t in threads:
        t.join()
