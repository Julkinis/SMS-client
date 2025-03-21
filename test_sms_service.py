import os
import pytest
import tempfile
from pathlib import Path

from sms_client.config import Config
from sms_client.http_protocol import HTTPRequest, HTTPResponse
from sms_client.cli import parse_arguments


def test_config_initialization():
    # Create a temporary config file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.toml') as temp_config:
        temp_config.write(
    '''
    [service]
    url = "http://testhost/send_sms"

    [auth]
    username = "test_user"
    password = "test_pass"

    [logging]
    level = "DEBUG"
    file = "test.log"
    ''')
        temp_config.close()
        
        config = Config(Path(temp_config.name))
        
        assert config.service_url == "http://testhost/send_sms"
        assert config.username == "test_user"
        assert config.password == "test_pass"

        os.unlink(temp_config.name)


def test_config_partial_credentials():
    # Create a temporary config file with missing password
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.toml') as temp_config:
        temp_config.write(
    '''
    [service]
    url = "http://testhost/send_sms"

    [auth]
    username = "test_user"

    [logging]
    level = "DEBUG"
    file = "test.log"
    ''')
        temp_config.close()
        
        with pytest.raises(ConnectionError):
            config = Config(Path(temp_config.name))
            config.password

        os.unlink(temp_config.name)
        

def test_http_request_to_bytes():
    # Test conversion of HTTP request to bytes
    request = HTTPRequest(
        method="POST", 
        path="/send_sms", 
        headers={"Content-Type": "application/json"},
        body={"sender": "+1234567890", "recipient": "+9876543210", "message": "Test"}
    )
    
    request_bytes = request.to_bytes()
   
    request_text = request_bytes.decode('utf-8')
    assert "POST /send_sms HTTP/1.1" in request_text
    assert "Content-Type: application/json" in request_text
    assert '"sender": "+1234567890"' in request_text


def test_http_request_from_bytes():
    # Test parsing of HTTP request from bytes
    raw_request = b"""POST /send_sms HTTP/1.1
    Content-Type: application/json
    Authorization: Basic dXNlcjpwYXNz

    {"sender": "+1234567890", "recipient": "+9876543210", "message": "Test"}"""

    request = HTTPRequest.from_bytes(raw_request)

    assert request.method == "POST"
    assert request.path == "/send_sms"
    assert request.headers["Content-Type"] == "application/json"
    assert request.body["sender"] == "+1234567890"


def test_http_response_to_bytes():
    # Test conversion of HTTP response to bytes 
    response = HTTPResponse(
        status_code=200, 
        headers={"Content-Type": "application/json"},
        body={"status": "success", "message_id": "12345"}
    )
    
    response_bytes = response.to_bytes()
    
    response_text = response_bytes.decode('utf-8')
    assert "200 OK" in response_text
    assert "Content-Type: application/json" in response_text
    assert '"status": "success"' in response_text


def test_http_response_from_bytes():
    # Test parsing of HTTP response from bytes
    raw_response = b"""HTTP/1.1 200 OK
Content-Type: application/json

{"status": "success", "message_id": "12345"}"""
    
    response = HTTPResponse.from_bytes(raw_response)
    
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    assert response.body["status"] == "success"


def test_argument_parsing():
    # Test argument parsing
    args = parse_arguments([
        "-s", "+1234567890", 
        "-r", "+9876543210", 
        "-m", "Test message",
        "-c", "test_config.toml"
    ])
    
    assert args.sender == "+1234567890"
    assert args.recipient == "+9876543210"
    assert args.message == "Test message"
    assert args.config == Path("test_config.toml")


def test_argument_parsing_missing_required():
    # Test missing required
    with pytest.raises(SystemExit):
        parse_arguments(["-s", "+1234567890"]) 


def test_argument_parsing_invalid_config_path():
    # Test invalid config path
    args = parse_arguments([
        "-s", "+1234567890", 
        "-r", "+9876543210", 
        "-m", "Test message",
        "-c", "non_existent_config.toml"
    ])
    
    assert args.config == Path("non_existent_config.toml")
