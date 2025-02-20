import os
import http.server
import socketserver
import threading
import time
import logging
from contextlib import contextmanager
from pyngrok import ngrok
from typing import Optional
import socket

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class NonBlockingTCPServer(socketserver.TCPServer):
    def __init__(self, *args, **kwargs):
        self.timeout = 1
        super().__init__(*args, **kwargs)
        self.socket.settimeout(1)
        self.allow_reuse_address = True

    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)

    def shutdown(self):
        self.socket.close()

class ServerManager:
    _instance: Optional['ServerManager'] = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ServerManager, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        self.PORT = 8000
        self._server = None
        self._server_thread = None
        self._ngrok_tunnel = None
        self._public_url = None
        self._ref_count = 0
        self._server_lock = threading.Lock()
        self._running = threading.Event()

    def serve_forever(self, httpd):
        self._running.set()
        while self._running.is_set():
            try:
                httpd.handle_request()
            except (socket.timeout, socket.error):
                continue
            except Exception as e:
                if self._running.is_set():
                    logger.error(f"Error in server loop: {e}")
        logger.debug("Server loop finished")

    def start_server(self):
        with self._server_lock:
            if self._server is not None:
                logger.debug("Server already running")
                return

            try:
                logger.debug("Starting server...")
                handler = SimpleHTTPRequestHandlerNoListing
                self._server = NonBlockingTCPServer(("", self.PORT), handler)
                self._server_thread = threading.Thread(target=self.serve_forever, 
                                                    args=(self._server,))
                self._server_thread.daemon = True
                self._server_thread.start()
                logger.debug("Server started successfully")
            except Exception as e:
                self._server = None
                self._server_thread = None
                self._running.clear()
                raise RuntimeError(f"Failed to start server: {e}")

    def start_ngrok(self):
        with self._server_lock:
            if self._ngrok_tunnel is None:
                logger.debug("Starting ngrok tunnel...")
                self._ngrok_tunnel = ngrok.connect(self.PORT)
                self._public_url = self._ngrok_tunnel.public_url
                logger.debug(f"Ngrok tunnel established at {self._public_url}")

    def cleanup(self):
        """Forcefully cleanup all resources"""
        logger.debug("Starting forceful cleanup...")
        
        # First, stop the server loop
        self._running.clear()
        
        # Force disconnect ngrok
        if self._ngrok_tunnel:
            try:
                logger.debug("Force disconnecting ngrok...")
                ngrok.disconnect(self._public_url)
            except Exception as e:
                logger.error(f"Error during ngrok disconnect: {e}")
            finally:
                self._ngrok_tunnel = None
                self._public_url = None
        
        # Force close the server
        if self._server:
            try:
                logger.debug("Force closing server...")
                self._server.shutdown()
                self._server.server_close()
            except Exception as e:
                logger.error(f"Error during server shutdown: {e}")
            finally:
                self._server = None
        
        self._server_thread = None
        logger.debug("Forceful cleanup completed")

    def stop_server(self):
        with self._server_lock:
            if self._server is not None and self._ref_count == 0:
                self.cleanup()

    def stop_ngrok(self):
        with self._server_lock:
            if self._ngrok_tunnel is not None and self._ref_count == 0:
                self.cleanup()

    def get_file_url(self, filename: str) -> str:
        return f"{self._public_url}/{filename}"

    def increment_ref(self):
        with self._server_lock:
            self._ref_count += 1
            logger.debug(f"Reference count increased to {self._ref_count}")

    def decrement_ref(self):
        with self._server_lock:
            self._ref_count -= 1
            logger.debug(f"Reference count decreased to {self._ref_count}")
            if self._ref_count == 0:
                self.cleanup()

class SimpleHTTPRequestHandlerNoListing(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_error(403, "Directory listing forbidden")
            return
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def log_message(self, format, *args):
        logger.debug(f"{self.client_address[0]} - - [{self.log_date_time_string()}] {format%args}")

@contextmanager
def exposeRemote(filepath: str):
    """
    Context manager that exposes a local file through a public ngrok URL.
    Multiple files can be exposed simultaneously using the same server.
    
    Args:
        filepath (str): Path to the local file to expose
    
    Yields:
        str: Public ngrok URL where the file can be accessed
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File {filepath} not found")
    
    logger.debug(f"Exposing file: {filepath}")
    original_dir = os.getcwd()
    file_dir = os.path.dirname(os.path.abspath(filepath))
    filename = os.path.basename(filepath)
    
    manager = ServerManager()
    
    try:
        os.chdir(file_dir)
        logger.debug(f"Changed directory to: {file_dir}")
        
        manager.increment_ref()
        manager.start_server()
        manager.start_ngrok()
        
        file_url = manager.get_file_url(filename)
        logger.debug(f"File available at: {file_url}")
        
        try:
            yield file_url
        finally:
            logger.debug("Context manager cleanup started")
            manager.decrement_ref()
            logger.debug("Context manager cleanup completed")
            
    finally:
        os.chdir(original_dir)
        logger.debug(f"Restored directory to: {original_dir}")
