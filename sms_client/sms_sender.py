import socket
import ssl
import logging
import urllib.parse
from typing import Dict, Any, Tuple, Optional

from .http_protocol import HTTPRequest, HTTPResponse
from .config import Config
from .logger import log_request, log_response


class SMSSender:
    
    def __init__(self, config: Config, logger: Optional[logging.Logger] = None):
   
        self.config = config
        self.logger = logger
        
        url_parts = urllib.parse.urlparse(self.config.service_url)
        self.protocol = url_parts.scheme
        self.host = url_parts.netloc
        self.path = url_parts.path or "/"      

        if ":" in self.host:
            self.host = self.host.split(":")[0]

        self.port = url_parts.port or 80

        # url = "http://localhost:4010/send_sms"
        # protocol = "http"
        # host = "localhost"
        # path = "/send_sms"
        # port = 4010
     
    def send_sms(
        self, sender: str, recipient: str, message: str
    ) -> Tuple[int, Dict[str, Any]]:
       
        if not sender or not recipient or not message:
            return 400, {"error": "Invalid parameters"}

        request_data = {
            "sender": sender,
            "recipient": recipient,
            "message": message
        }

        try:
            username = self.config.username
            password = self.config.password
        except ConnectionError:
            self.logger.error(f"Authentication failed: status_code=401, error=Invalid credentials")
            return 401, {"error": "Invalid credentials"}
        
        log_request(self.logger, request_data)
        
        request = HTTPRequest(
            method="POST",
            path=self.path,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Host": self.host
            },
            body=request_data,
            host=self.host
        ) 
        # Add authorization header
        request.set_basic_auth(username, password)
        
        try:
            response = self._send_request(request)
            log_body = response.body if response.body is not None else {}
            self.logger.info(f"Received response: status_code={response.status_code}, body={log_body}")
        
            return response.status_code, response.body or {}
        
        except Exception as e:
            self.logger.error(f"Request failed: {e},  status_code=500")
            return 500, {"error": f"Internal server error: {str(e)}"}
   
   
    def _send_request(self, request: HTTPRequest) -> HTTPResponse:
        # Using TCP socket to connect to the server
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            # if self.protocol == "https":
            #     context = ssl.create_default_context()
            #     sock = context.wrap_socket(sock, server_hostname=self.host)
            
            sock.connect((self.host, self.port))
            request_bytes = request.to_bytes()
            sock.sendall(request_bytes)
            # Receive response data
            response_data = sock.recv(4096)
            response = HTTPResponse.from_bytes(response_data)
            return response
        
        finally:
            sock.close()
            