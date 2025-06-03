"""
Configuration management for K1NGB0B Recon Script.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class ToolConfig:
    """Configuration for individual reconnaissance tools."""
    enabled: bool = True
    timeout: int = 300
    retries: int = 3
    additional_args: list = field(default_factory=list)


@dataclass
class OutputConfig:
    """Configuration for output handling."""
    base_dir: str = "."
    create_reports: bool = True
    save_raw_data: bool = True
    compress_results: bool = False
    format: str = "txt"  # txt, json, csv


@dataclass
class HttpConfig:
    """Configuration for HTTP requests."""
    timeout: int = 10
    retries: int = 3
    threads: int = 50
    user_agent: str = "K1NGB0B-Recon/2.0"


class Config:
    """Main configuration class for the reconnaissance tool."""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize configuration with default values."""
        self.tools = {
            'assetfinder': ToolConfig(),
            'subfinder': ToolConfig(),
            'crt_sh': ToolConfig(timeout=60),
            'wayback': ToolConfig(timeout=120),
            'httpx': ToolConfig()
        }
        
        self.output = OutputConfig()
        self.http = HttpConfig()
        self.verbose = False
        self.debug = False
        
        # Load configuration from file if provided
        if config_file:
            self.load_from_file(config_file)
    
    def load_from_file(self, config_file: str) -> None:
        """Load configuration from YAML file."""
        try:
            config_path = Path(config_file)
            if not config_path.exists():
                raise FileNotFoundError(f"Configuration file not found: {config_file}")
            
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f)
            
            self._update_from_dict(config_data)
            
        except Exception as e:
            raise ValueError(f"Error loading configuration: {e}")
    
    def _update_from_dict(self, config_data: Dict[str, Any]) -> None:
        """Update configuration from dictionary."""
        # Update tool configurations
        if 'tools' in config_data:
            for tool_name, tool_config in config_data['tools'].items():
                if tool_name in self.tools:
                    for key, value in tool_config.items():
                        if hasattr(self.tools[tool_name], key):
                            setattr(self.tools[tool_name], key, value)
        
        # Update output configuration
        if 'output' in config_data:
            for key, value in config_data['output'].items():
                if hasattr(self.output, key):
                    setattr(self.output, key, value)
        
        # Update HTTP configuration
        if 'http' in config_data:
            for key, value in config_data['http'].items():
                if hasattr(self.http, key):
                    setattr(self.http, key, value)
        
        # Update general settings
        self.verbose = config_data.get('verbose', self.verbose)
        self.debug = config_data.get('debug', self.debug)
    
    def save_to_file(self, config_file: str) -> None:
        """Save current configuration to YAML file."""
        config_data = {
            'tools': {
                name: {
                    'enabled': tool.enabled,
                    'timeout': tool.timeout,
                    'retries': tool.retries,
                    'additional_args': tool.additional_args
                }
                for name, tool in self.tools.items()
            },
            'output': {
                'base_dir': self.output.base_dir,
                'create_reports': self.output.create_reports,
                'save_raw_data': self.output.save_raw_data,
                'compress_results': self.output.compress_results,
                'format': self.output.format
            },
            'http': {
                'timeout': self.http.timeout,
                'retries': self.http.retries,
                'threads': self.http.threads,
                'user_agent': self.http.user_agent
            },
            'verbose': self.verbose,
            'debug': self.debug
        }
        
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False, indent=2)
    
    def get_tool_config(self, tool_name: str) -> ToolConfig:
        """Get configuration for a specific tool."""
        return self.tools.get(tool_name, ToolConfig())
    
    def is_tool_enabled(self, tool_name: str) -> bool:
        """Check if a tool is enabled."""
        return self.tools.get(tool_name, ToolConfig()).enabled
    
    @classmethod
    def create_default_config(cls, config_file: str) -> 'Config':
        """Create a default configuration file."""
        config = cls()
        config.save_to_file(config_file)
        return config
