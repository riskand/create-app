# myapp/deployer/validators.py
"""
MyApp specific validators
"""
import json
import logging
import os

logger = logging.getLogger(__name__)


class MyAppEnvironmentValidator:
    """Validates MyApp specific environment variables (SRP)"""

    REQUIRED_VARS = [
        'MYAPP_REQUIRED_VAR',
        'MYAPP_SETTING',
    ]

    def validate(self) -> bool:
        """Validate MyApp environment variables"""
        logger.info("Validating MyApp environment variables...")

        # Check required variables
        missing_vars = []
        for var in self.REQUIRED_VARS:
            if not os.getenv(var):
                missing_vars.append(var)

        if missing_vars:
            logger.error(f"❌ Missing environment variables: {', '.join(missing_vars)}")
            logger.info("💡 Please check your .env file")
            return False

        logger.info("✅ All required environment variables found")

        # Check feature flags (optional)
        feature_vars = [var for var in os.environ.keys() if var.startswith('MYAPP_FEATURE_')]
        if feature_vars:
            logger.info(f"✅ Found {len(feature_vars)} feature flag(s)")

        return True


class MyAppConfigValidator:
    """Validates MyApp configuration (SRP)"""

    def validate(self) -> bool:
        """Validate MyApp configuration"""
        logger.info("Validating MyApp configuration...")

        # Add your configuration validation logic here
        # Example: Check if API endpoints are reachable
        # Example: Validate file paths
        # Example: Check database connections

        logger.info("✅ Configuration validation passed")
        return True