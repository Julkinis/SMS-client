# SMS Client CLI

## Project Description

A CLI application for sending SMS messages through an external service using basic HTTP authentication.

## Technical Characteristics

- Sending SMS via HTTP API
- Basic authentication
- Flexible configuration via TOML
- Comprehensive logging

## Configuration

`config.toml` file with the following structure:

```toml
[service]
url = "http://sms-service.com/send_sms"

[auth]
username = "username"
password = "password"

[logging]
level = "INFO"
file = "sms_client.log"
```

### Configuration Parameters
- `url`: SMS service endpoint
- `username`: Authentication login
- `password`: Authentication password
- `level`: Logging level
- `file`: Path to log file

## Usage

Install the Package

```bash
pip install .
``` 

```bash
sms-client -s "+1234567890" -r "+9876543210" -m "Your message"
```

### Command-Line Parameters
- `-s` or `--sender`: Sender's phone number (required)
- `-r` or `--recipient`: Recipient's phone number (required)
- `-m` or `--message`: Message text (required)
- `-c` or `--config`: Path to configuration file (optional)

## Architecture

### Modules
- `cli.py`: Command-line parameters processing
- `config.py`: Configuration management
- `http_protocol.py`: HTTP request and response implementation
- `sms_sender.py`: SMS sending logic
- `logger.py`: Logging setup

### Key Classes
- `HTTPRequest`: HTTP request representation
  - Methods:
    - `to_bytes()`: Convert to bytes
    - `from_bytes()`: Create from bytes
- `HTTPResponse`: HTTP response representation
  - Similar methods

## Development and Testing

### Running Tests
```bash
pytest
```
