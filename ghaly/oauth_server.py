"""
OAuth callback server for handling GitHub OAuth redirects.

This module provides a simple HTTP server to automatically capture
OAuth authorization codes from the callback URL.
"""

import http.server
import socketserver
import threading
import webbrowser
from typing import Callable, Optional


class OAuthCallbackHandler(http.server.BaseHTTPRequestHandler):
    """HTTP request handler for OAuth callback."""
    
    def __init__(self, *args, callback_received: Callable[[str, Optional[str]], None], **kwargs):
        self.callback_received = callback_received
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET request for OAuth callback."""
        if self.path.startswith('/callback'):
            query = self.path.split('?', 1)[1] if '?' in self.path else ''
            params = {}
            
            for param in query.split('&'):
                if '=' in param:
                    key, value = param.split('=', 1)
                    params[key] = value
            
            code = params.get('code')
            state = params.get('state')
            
            if code:
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                
                html_content = """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Authentication Successful</title>
                    <style>
                        body {
                            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            height: 100vh;
                            margin: 0;
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        }
                        .container {
                            text-align: center;
                            background: white;
                            padding: 40px;
                            border-radius: 10px;
                            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                        }
                        h1 {
                            color: #333;
                            margin-bottom: 20px;
                        }
                        p {
                            color: #666;
                            font-size: 16px;
                        }
                        .success-icon {
                            font-size: 64px;
                            margin-bottom: 20px;
                        }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="success-icon">✅</div>
                        <h1>Authentication Successful!</h1>
                        <p>You can close this window and return to the terminal.</p>
                    </div>
                </body>
                </html>
                """
                
                self.wfile.write(html_content.encode('utf-8'))
                
                self.callback_received(code, state)
            else:
                self.send_error(400, "Missing authorization code")
        else:
            self.send_error(404, "Not found")
    
    def log_message(self, format, *args):
        """Suppress default logging."""
        pass


class OAuthCallbackServer:
    """Simple HTTP server for OAuth callback handling."""
    
    def __init__(self, port: int = 8080):
        """
        Initialize the OAuth callback server.
        
        Args:
            port: Port number to listen on
        """
        self.port = port
        self.server: Optional[socketserver.TCPServer] = None
        self.server_thread: Optional[threading.Thread] = None
        self.auth_code: Optional[str] = None
        self.state: Optional[str] = None
        self.received = threading.Event()
    
    def _handler_factory(self):
        """Create handler factory with callback."""
        def handler(*args, **kwargs):
            return OAuthCallbackHandler(*args, callback_received=self._on_callback, **kwargs)
        return handler
    
    def _on_callback(self, code: str, state: Optional[str]) -> None:
        """
        Handle OAuth callback.
        
        Args:
            code: Authorization code
            state: State parameter
        """
        self.auth_code = code
        self.state = state
        self.received.set()
    
    def start(self) -> None:
        """Start the callback server."""
        try:
            handler = self._handler_factory()
            self.server = socketserver.TCPServer(('0.0.0.0', self.port), handler)
            self.server.allow_reuse_address = True
            
            self.server_thread = threading.Thread(target=self.server.serve_forever)
            self.server_thread.daemon = True
            self.server_thread.start()
            
        except OSError as e:
            if e.errno == 48:
                raise OAuthServerError(
                    f"Port {self.port} is already in use. "
                    "Please ensure no other application is using this port."
                )
            else:
                raise OAuthServerError(f"Failed to start server: {e}")
    
    def wait_for_callback(self, timeout: int = 120) -> tuple[Optional[str], Optional[str]]:
        """
        Wait for OAuth callback.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            Tuple of (auth_code, state) or (None, None) if timeout
        """
        if self.received.wait(timeout=timeout):
            return self.auth_code, self.state
        return None, None
    
    def stop(self) -> None:
        """Stop the callback server."""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
        if self.server_thread:
            self.server_thread.join(timeout=5)


class OAuthServerError(Exception):
    """Exception raised for OAuth server errors."""
    pass


def start_callback_server(port: int = 8080, timeout: int = 120) -> tuple[Optional[str], Optional[str]]:
    """
    Start callback server and wait for OAuth callback.
    
    Args:
        port: Port number to listen on
        timeout: Maximum time to wait in seconds
        
    Returns:
        Tuple of (auth_code, state) or (None, None) if timeout
        
    Raises:
        OAuthServerError: If server fails to start
    """
    server = OAuthCallbackServer(port)
    server.start()
    
    try:
        return server.wait_for_callback(timeout=timeout)
    finally:
        server.stop()
