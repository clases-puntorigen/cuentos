import os
import http.server
import socketserver
import threading
from contextlib import contextmanager
from pyngrok import ngrok

class SimpleHTTPRequestHandlerNoListing(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_error(403, "Directory listing forbidden")
            return
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

@contextmanager
def exposeRemote(filepath):
    """
    Context manager that exposes a local file through a public ngrok URL.
    
    Args:
        filepath (str): Path to the local file to expose
    
    Yields:
        str: Public ngrok URL where the file can be accessed
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File {filepath} not found")
    
    # Store original working directory
    original_dir = os.getcwd()
    file_dir = os.path.dirname(os.path.abspath(filepath))
    filename = os.path.basename(filepath)
    
    # Create and start HTTP server in a separate thread
    PORT = 8000
    handler = SimpleHTTPRequestHandlerNoListing
    
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        # Start server in a separate thread
        server_thread = threading.Thread(target=httpd.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        
        try:
            # Change to file's directory
            os.chdir(file_dir)
            
            # Start ngrok tunnel
            public_url = ngrok.connect(PORT).public_url
            file_url = f"{public_url}/{filename}"
            
            try:
                yield file_url
            finally:
                # Disconnect ngrok tunnel
                ngrok.disconnect(public_url)
                
        finally:
            # Restore original working directory
            os.chdir(original_dir)
            # Shutdown the HTTP server
            httpd.shutdown()
            httpd.server_close()
