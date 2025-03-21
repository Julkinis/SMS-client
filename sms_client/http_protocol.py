import json
import base64
from typing import Dict, Optional, ClassVar, Any


class HTTPRequest:
    
    def __init__(
        self,
        method: str,
        path: str,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[Dict[str, Any]] = None,
        host: str = "",
        protocol: str = "HTTP/1.1"
    ):
        """
        Initialize HTTP request.
        
        Args:
            method: HTTP method 
            path: Request path
            headers: Optional dictionary of HTTP headers
            body: Optional request body as a dictionary
            host: Host for the request
            protocol: HTTP protocol version
        """
        self.method = method
        self.path = path
        self.headers = headers or {}
        self.body = body
        self.host = host
        self.protocol = protocol

        # Add Content-Type header if body is present
        if self.body and "Content-Type" not in self.headers:
            self.headers["Content-Type"] = "application/json"
    
    def set_basic_auth(self, username: str, password: str) -> None:
        credentials = f"{username}:{password}"
        encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
        # print(f"Original: {credentials}")
        # print(f"Encoded: {encoded_credentials}")
        self.headers["Authorization"] = f"Basic {encoded_credentials}"
    
    def to_bytes(self) -> bytes:
  
        request_lines = [f"{self.method} {self.path} {self.protocol}"]
       
        for key, value in self.headers.items():
            request_lines.append(f"{key}: {value}")
        
        if self.body:
            body_text = json.dumps(self.body)
            request_lines.append(f"Content-Length: {len(body_text)}")
            
            request_lines.append("")
            request_lines.append(body_text)
        else:
            request_lines.append("")
        
        return "\r\n".join(request_lines).encode()
        
    @classmethod
    def from_bytes(cls, binary_data: bytes) -> "HTTPRequest":

        request_text = binary_data.decode("utf-8")
        # print("Parsed text:", request_text)
        
        lines = request_text.split('\n')

        first_line = lines[0].split()
        method = first_line[0]
        path = first_line[1]

        headers = {}
        body_start_index = 0
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == '':
                body_start_index = i + 1
                break
            if ":" in line:
                key, value = line.split(":", 1)
                headers[key.strip()] = value.strip()
        
        body = None
        body_lines = lines[body_start_index:]
        body_text = '\n'.join(body_lines).strip()
        
        if body_text:
            try:
                body = json.loads(body_text)
            except json.JSONDecodeError:
                body = body_text
        
        return cls(method, path, headers, body)


class HTTPResponse:
    
    status_messages: ClassVar[Dict[int, str]] = {
        200: "OK",
        400: "Bad Request",
        401: "Unauthorized",
        500: "Internal Server Error"
    }
    
    def __init__(
        self,
        status_code: int,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[Dict[str, Any]] = None,
        protocol: str = "HTTP/1.1"
    ):
        """
        Initialize HTTP response.
        
        Args:
            status_code: HTTP status code
            headers: Optional dictionary of HTTP headers
            body: Optional response body as a dictionary
            protocol: HTTP protocol version
        """
        self.status_code = status_code
        self.status_message = self.status_messages.get(status_code, "Unknown")
        self.headers = headers or {}
        self.body = body
        self.protocol = protocol
        
        # Add Content-Type header if body is present
        if self.body and "Content-Type" not in self.headers:
            self.headers["Content-Type"] = "application/json"
    
    def to_bytes(self) -> bytes:

        response_lines = [f"{self.protocol} {self.status_code} {self.status_message}"]
    
        for key, value in self.headers.items():
            response_lines.append(f"{key}: {value}")
        
        if self.body:
            body_text = json.dumps(self.body)
            response_lines.append(f"Content-Length: {len(body_text)}")
            
            response_lines.append("")
            response_lines.append(body_text)
        else:
            response_lines.append("")
        
        return "\r\n".join(response_lines).encode()
    
    @classmethod
    def from_bytes(cls, binary_data: bytes) -> "HTTPResponse":

        response_text = binary_data.decode("utf-8")
        lines = response_text.split('\n')
      
        first_line = lines[0].split()
        status_code = int(first_line[1])
        
        headers = {}
        body_start_index = 0
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == '':
                body_start_index = i + 1
                break
            if ":" in line:
                key, value = line.split(":", 1)
        
        body = None
        body_lines = lines[body_start_index:]
        body_text = '\n'.join(body_lines).strip()
        
        if body_text:
            try:
                body = json.loads(body_text)
            except json.JSONDecodeError:
                body = body_text
        
        return cls(status_code, headers, body)