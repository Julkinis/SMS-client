import logging
from typing import Optional, Dict, Any, Union


def setup_logger(
    log_level: str = "INFO",
    log_file: Optional[str] = None
) -> logging.Logger:
    
    logger = logging.getLogger("sms_client")
    
    # Set log level, default to INFO
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    logger.setLevel(numeric_level)
    
    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Create file handler if log file is specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def log_request(logger: logging.Logger, request_data: Dict[str, Any]) -> None:
    """Log SMS request details.
    
    Args:
        logger: Logger to use
        request_data: Request data to log
    """
    logger.info(
        "Sending SMS: from=%s, to=%s, message=\"%s\"",
        request_data.get("sender", "unknown"),
        request_data.get("recipient", "unknown"),
        request_data.get("message", "")
    )


def log_response(
    logger: logging.Logger, 
    status_code: int, 
    body: Union[Dict[str, Any], str, None]
) -> None:
    """Log SMS response details.
    
    Args:
        logger: Logger to use
        status_code: HTTP status code
        body: Response body
    """
    logger.info("Received response: status_code=%d, body=%s", status_code, body)