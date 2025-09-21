import http.server
import socketserver
import backend
import markdown
import traceback
import os
from urllib.parse import urlparse, parse_qs

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Parse the URL and query parameters
        parsed_path = urlparse(self.path)
        query_params = parse_qs(parsed_path.query)

        # Serve static files from /static/
        if parsed_path.path.startswith('/static/'):
            static_file_path = os.path.join(os.getcwd(), parsed_path.path.lstrip('/'))
            if os.path.isfile(static_file_path):
                self.send_response(200)
                # Set correct content type for PNG
                if static_file_path.endswith('.png'):
                    self.send_header('Content-type', 'image/png')
                elif static_file_path.endswith('.jpg') or static_file_path.endswith('.jpeg'):
                    self.send_header('Content-type', 'image/jpeg')
                else:
                    self.send_header('Content-type', 'application/octet-stream')
                self.end_headers()
                with open(static_file_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'<h1>404 - Static File Not Found</h1>')
            return

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
        print(self.path)
        if self.path == '/api/data':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = f'{{"received_data": "{post_data.decode()}", "method": "POST"}}'
            self.wfile.write(response.encode('utf-8'))
        elif self.path == '/api/generate_story':
            import json
            try:
                data = json.loads(post_data)
                topic = data.get('topic', 'default topic')
                language = data.get('language', 'English')
                world_file = data.get('world_file', 'data/world0.json')
                current_content_idx = data.get('current_content_idx', 'new')
                prompt_base = backend.prompt_bases[0]  # Use story prompt
                story, ended = backend.generate_content(prompt_base, topic, language, world_file, current_content_idx)
                response = {"story": story, "ended": ended}
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(markdown.markdown(story).encode('utf-8'))
                # print(story)
                #self.wfile.write(markdown.markdown(story.encode('utf-8')))
            except Exception as e:
                print(traceback.format_exc())
                print("Error generating story:", e)
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
        elif self.path == '/api/clear_worlds':
            import json
            import glob
            try:
                # Find all JSON files in the data directory
                world_files = glob.glob('data/*.json')
                cleared_worlds = []
                
                for world_file in world_files:
                    # Extract world name from file path (e.g., 'data/world0.json' -> 'world0')
                    world_name = os.path.basename(world_file).replace('.json', '')
                    backend.clear_world(world_name)
                    cleared_worlds.append(world_name)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {
                    "success": True,
                    "message": f"Successfully cleared {len(cleared_worlds)} world(s)",
                    "cleared_worlds": cleared_worlds
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
            except Exception as e:
                print(traceback.format_exc())
                print("Error clearing worlds:", e)
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {"success": False, "error": str(e)}
                self.wfile.write(json.dumps(response).encode('utf-8'))
        elif self.path == '/api/translate':
            import json
            import requests
            try:
                data = json.loads(post_data)
                text = data.get('text', '')
                source_lang = data.get('source', 'auto')  # Auto-detect source language
                target_lang = data.get('target', 'en')    # Default to English
                
                if not text.strip():
                    raise ValueError("No text provided for translation")
                
                # Use Free Translate API from ftapi.pythonanywhere.com
                base_url = "https://ftapi.pythonanywhere.com/translate"
                
                # Build URL parameters - use auto-detect if source is 'auto'
                if source_lang == 'auto':
                    # Use the auto-detect method (second way - only dl and text)
                    url = f"{base_url}?dl={target_lang}&text={requests.utils.quote(text)}"
                else:
                    # Use the explicit source language method (first way - sl, dl, and text)
                    url = f"{base_url}?sl={source_lang}&dl={target_lang}&text={requests.utils.quote(text)}"
                
                # Make request to Free Translate API
                response = requests.get(url, timeout=15)
                
                if response.status_code == 200:
                    result = response.json()
                    translated_text = result.get('destination-text', '')
                    detected_source = result.get('source-language', source_lang)
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    
                    response_data = {
                        "success": True,
                        "original_text": text,
                        "translated_text": translated_text,
                        "source_language": detected_source,
                        "target_language": target_lang,
                        "pronunciation": result.get('pronunciation', {}),
                        "additional_translations": result.get('translations', {}).get('possible-translations', [])
                    }
                    self.wfile.write(json.dumps(response_data).encode('utf-8'))
                else:
                    raise Exception(f"Translation API returned status {response.status_code}: {response.text}")
                    
            except requests.RequestException as e:
                print(f"Network error during translation: {e}")
                self.send_response(503)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {"success": False, "error": "Translation service unavailable"}
                self.wfile.write(json.dumps(response).encode('utf-8'))
            except Exception as e:
                print(traceback.format_exc())
                print("Error translating text:", e)
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {"success": False, "error": str(e)}
                self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"error": "POST endpoint not found"}')

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
    # Default port is 7000, but you can change it here
    PORT = 7003
    start_server(PORT)