"""Command-line interface for SMS client."""
import argparse
import sys
import json
from pathlib import Path
from typing import List, Optional

from .config import Config
from .sms_sender import SMSSender
from .logger import setup_logger


def parse_arguments(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="SMS client for sending SMS messages"
    )
    
    # The config file is an optional argument.
    parser.add_argument(
        "--config",
        "-c",
        type=Path,
        default=Path("config.toml"),
        help="Path to configuration file (default: config.toml)"
    )
    
    # The sender is a required argument.
    parser.add_argument(
        "--sender",
        "-s",
        required=True,
        help="Sender phone number"
    )
    
    # The recipient is a required argument.
    parser.add_argument(
        "--recipient",
        "-r",
        required=True,
        help="Recipient phone number"
    )
    
    # The message is a required argument.
    parser.add_argument(
        "--message",
        "-m",
        required=True,
        help="SMS message text"
    )
    
    return parser.parse_args(args)


def main(args: Optional[List[str]] = None) -> int:
    """Main entry point for the application."""
    logger = None
    
    try:
        parsed_args = parse_arguments(args)

        config = Config(parsed_args.config)

        logger = setup_logger(
            log_level=config.config_data.get("logging", {}).get("level", "INFO"),
            log_file=config.config_data.get("logging", {}).get("file")
        )
        
        logger.info(
            "Starting SMS client: sender=%s, recipient=%s, message=\"%s\"",
            parsed_args.sender,
            parsed_args.recipient,
            parsed_args.message
        )
        
        try:
            sms_sender = SMSSender(config, logger)
        except Exception as e:
            logger.error(str(e))
            return
        
        status_code, response_body = sms_sender.send_sms(
            parsed_args.sender,
            parsed_args.recipient,
            parsed_args.message
        )
        
        print(f"Status Code: {status_code}")
        if response_body:
            if isinstance(response_body, dict):
                print(f"Response Body: {json.dumps(response_body, indent=2)}")
            else:
                print(f"Response Body: {response_body}")

        return 0 if status_code == 200 else 1
    
    except Exception as e:
        logger.exception("Critical error during execution")
        
        print(f"Critical error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
