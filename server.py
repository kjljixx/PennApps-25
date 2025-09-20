import http.server
import socketserver
import backend
import os
from urllib.parse import urlparse, parse_qs

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Parse the URL and query parameters
        parsed_path = urlparse(self.path)
        query_params = parse_qs(parsed_path.query)
        
        # Handle different routes
        if parsed_path.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            # Read and serve the duo.html file
            try:
                with open('duo.html', 'r', encoding='utf-8') as file:
                    html_content = file.read()
                self.wfile.write(html_content.encode('utf-8'))
            except FileNotFoundError:
                error_html = """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>File Not Found</title>
                </head>
                <body>
                    <h1>Error: duo.html not found</h1>
                    <p>Please make sure duo.html exists in the same directory as server.py</p>
                </body>
                </html>
                """
                self.wfile.write(error_html.encode('utf-8'))
            
        elif parsed_path.path == '/hello':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Hello from Python server!')
            
        elif parsed_path.path == '/api/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = '{"status": "running", "message": "Server is healthy"}'
            self.wfile.write(response.encode('utf-8'))
            
        elif parsed_path.path == '/api/echo':
            message = query_params.get('message', ['No message provided'])[0]
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = f'{{"echo": "{message}"}}'
            self.wfile.write(response.encode('utf-8'))
            
        else:
            # Handle 404 for unknown paths
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<h1>404 - Page Not Found</h1>')

    def do_POST(self):
        # Handle POST requests
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        if self.path == '/api/data':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = f'{{"received_data": "{post_data.decode()}", "method": "POST"}}'
            self.wfile.write(response.encode('utf-8'))
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'POST endpoint not found')

def start_server(port=8000):
    """Start the HTTP server on the specified port"""
    try:
        with socketserver.TCPServer(("", port), MyHTTPRequestHandler) as httpd:
            print(f"Server starting on http://localhost:{port}")
            print("Press Ctrl+C to stop the server")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"Port {port} is already in use. Trying port {port + 1}...")
            start_server(port + 1)
        else:
            print(f"Error starting server: {e}")

if __name__ == "__main__":
    # Default port is 8000, but you can change it here
    PORT = 8000
    start_server(PORT)