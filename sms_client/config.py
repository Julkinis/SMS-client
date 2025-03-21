import tomli
from pathlib import Path
from typing import Dict, Any, Optional


class Config:

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path("./config.toml")
        self.config_data: Dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self) -> None:
        try:
            with open(self.config_path, "rb") as f:
                self.config_data = tomli.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        except tomli.TOMLDecodeError:
            raise ValueError(f"Invalid TOML format in configuration file: {self.config_path}")
    
    @property
    def service_url(self) -> str:
        try:
            url = self.config_data.get("service", {}).get("url")
            if not url:
                raise ValueError("Service URL is empty")
            return url
        except (KeyError, ValueError):
            raise ConnectionError("Service URL not found in configuration")
    
    @property
    def username(self) -> str:
        try:
            username = self.config_data.get("auth", {}).get("username")
            if not username:
                raise ValueError("No username provided")
            return username
        except (KeyError, ValueError):
            raise ConnectionError("Invalid credentials")
        
    @property
    def password(self) -> str:
        try:
            password = self.config_data.get("auth", {}).get("password")
            if not password:
                raise ValueError("No password provided")
            return password
        except (KeyError, ValueError):
            raise ConnectionError("Invalid credentials")
        