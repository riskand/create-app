# myapp/config.py
import logging
import os
import pathlib
from typing import Dict, List

logger = logging.getLogger(__name__)


class Config:
    """Configuration management using environment variables"""

    def __init__(self, config_dir: pathlib.Path = None):
        self.config_dir = config_dir

        # Load application-specific .env file
        self._load_application_env()

        # Initialize your configuration here
        self.app_setting = self._get_app_setting()
        self.feature_flags = self._get_feature_flags()

        logger.info(f"Configuration loaded with app_setting: {self.app_setting}")

    def _load_application_env(self):
        """Load application-specific .env file"""
        try:
            from dotenv import load_dotenv

            # Try multiple locations in order
            env_paths = [
                pathlib.Path(__file__).parent / '.env',  # myapp/.env
                pathlib.Path.cwd() / '.env',  # Current directory .env
                pathlib.Path.cwd() / 'myapp' / '.env',  # myapp/.env from root
            ]

            loaded = False
            for env_path in env_paths:
                if env_path.exists():
                    load_dotenv(env_path, override=True)
                    logger.info(f"✅ Loaded application config from {env_path}")
                    loaded = True
                    break

            if not loaded:
                logger.info("ℹ️  No application .env file found, using system environment")
        except ImportError:
            logger.info("ℹ️  python-dotenv not installed, using system environment variables")

    def _get_app_setting(self) -> str:
        """Get application setting from environment"""
        setting = os.getenv('MYAPP_SETTING', 'default_value')
        logger.debug(f"Using app_setting: {setting}")
        return setting

    def _get_feature_flags(self) -> Dict[str, bool]:
        """Get feature flags from environment variables"""
        flags = {}
        
        # Example: Get all MYAPP_FEATURE_* environment variables
        for env_var, value in os.environ.items():
            if env_var.startswith('MYAPP_FEATURE_'):
                feature_name = env_var[14:].lower()  # Remove 'MYAPP_FEATURE_' prefix
                flags[feature_name] = value.lower() in ['true', '1', 'yes']
                logger.debug(f"Feature flag {feature_name}: {flags[feature_name]}")

        return flags

    def _validate_config(self):
        """Validate configuration"""
        required_vars = ['MYAPP_REQUIRED_VAR']
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)

        if missing_vars:
            error_msg = f"❌ Missing required environment variables: {missing_vars}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        logger.info("✅ Configuration validation passed")

    def get_setting(self, key: str, default=None):
        """Get a configuration setting"""
        return os.getenv(f'MYAPP_{key.upper()}', default)
