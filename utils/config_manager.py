"""
Configuration Manager

This module handles centralized configuration management for the cryptocurrency analysis application.
"""

import os
import yaml
from typing import Dict, Any

class ConfigManager:
    """Centralized configuration management class."""
    
    def __init__(self, config_file: str):
        """Initialize the configuration manager with the path to the config file."""
        self.config_file = config_file
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load and process configuration from YAML file."""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
            
            # Convert relative paths to absolute paths
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config['csv_file_path'] = os.path.join(base_dir, config['csv_file_path'])
            config['output_dir'] = os.path.join(base_dir, config['output_dir'])
            
            return config
        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration: {str(e)}")
    
    def get_config(self) -> Dict[str, Any]:
        """Get the full configuration dictionary."""
        return self.config
    
    def get_value(self, key: str) -> Any:
        """Get a specific configuration value."""
        return self.config.get(key)


class ConfigurationError(Exception):
    """Custom exception for configuration-related errors."""
    pass
