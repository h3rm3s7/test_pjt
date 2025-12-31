"""
Configuration Manager Module
Load and manage configuration settings
"""

import yaml
import os
from typing import Dict, Any, Optional


class ConfigManager:
    """Manage configuration settings"""

    def __init__(self, config_path: str = 'config.yaml'):
        self.config_path = config_path
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from YAML file

        Returns:
            Configuration dictionary
        """
        if not os.path.exists(self.config_path):
            print(f"⚠ Config file not found: {self.config_path}")
            return self._get_default_config()

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                print(f"✓ Loaded configuration from {self.config_path}")
                return config
        except Exception as e:
            print(f"⚠ Error loading config: {str(e)}")
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'llm': {
                'provider': 'openai',
                'model': 'gpt-4',
                'temperature': 0.7,
                'max_tokens': 2000,
                'api_key_env': 'OPENAI_API_KEY'
            },
            'data': {
                'input_path': 'data/raw',
                'processed_path': 'data/processed',
                'encoding': 'utf-8',
                'date_format': '%Y-%m-%d'
            },
            'kpi_thresholds': {
                'performance': {
                    'aht_target': 300,
                    'fcr_target': 0.85,
                    'service_level_target': 0.80
                },
                'quality': {
                    'qa_score_target': 90,
                    'csat_target': 4.0,
                    'nps_target': 50
                }
            },
            'analysis': {
                'correlation_threshold': 0.3,
                'outlier_std': 3,
                'min_data_points': 30
            },
            'report': {
                'output_path': 'outputs',
                'format': 'docx',
                'include_charts': True
            },
            'logging': {
                'level': 'INFO',
                'file': 'logs/app.log',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            }
        }

    def get(self, *keys, default=None) -> Any:
        """
        Get configuration value using dot notation

        Args:
            *keys: Configuration keys
            default: Default value if not found

        Returns:
            Configuration value
        """
        value = self.config
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
                if value is None:
                    return default
            else:
                return default
        return value

    def set(self, value: Any, *keys) -> None:
        """
        Set configuration value

        Args:
            value: Value to set
            *keys: Configuration keys
        """
        config = self.config
        for key in keys[:-1]:
            config = config.setdefault(key, {})
        config[keys[-1]] = value

    def save_config(self, path: Optional[str] = None) -> None:
        """
        Save configuration to file

        Args:
            path: Path to save (uses default if None)
        """
        save_path = path or self.config_path

        with open(save_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.config, f, default_flow_style=False)

        print(f"✓ Configuration saved to {save_path}")

    def update(self, updates: Dict[str, Any]) -> None:
        """
        Update configuration with new values

        Args:
            updates: Dictionary with updates
        """
        def deep_update(base_dict, update_dict):
            for key, value in update_dict.items():
                if isinstance(value, dict) and key in base_dict:
                    deep_update(base_dict[key], value)
                else:
                    base_dict[key] = value

        deep_update(self.config, updates)
        print("✓ Configuration updated")

    def __getitem__(self, key: str) -> Any:
        """Allow dictionary-style access"""
        return self.config[key]

    def __setitem__(self, key: str, value: Any) -> None:
        """Allow dictionary-style setting"""
        self.config[key] = value

    def to_dict(self) -> Dict[str, Any]:
        """Return configuration as dictionary"""
        return self.config.copy()
