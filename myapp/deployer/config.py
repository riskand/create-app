# myapp/deployer/config.py
"""
MyApp specific deployment configuration
"""
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Set

from lambda_deploy_tool.config import DeployConfig


@dataclass
class MyAppDeployConfig(DeployConfig):
    """MyApp specific deployment configuration"""

    # MyApp specific defaults
    function_name: str = 'myapp'
    role_name: str = 'myapp-lambda-role'
    schedule_name: str = 'myapp-schedule'
    schedule_expression: str = 'rate(1 hour)'  # Run every hour
    budget_name: str = 'MyApp Budget'

    # MyApp specific environment variable configuration
    required_env_vars: Set[str] = field(default_factory=lambda: {
        'MYAPP_REQUIRED_VAR',
        'MYAPP_SETTING',
    })

    allowed_env_prefixes: Set[str] = field(default_factory=lambda: {
        'MYAPP_FEATURE_',
    })

    def __post_init__(self):
        """Initialize MyApp specific configuration"""
        # Load deployment environment variables first
        self._load_deployment_env()

        # Override defaults with environment variables if set
        self._apply_env_overrides()

        # Call parent __post_init__
        super().__post_init__()

        # Validate budget email if enforcement is enabled
        if self.enable_budget:
            self._validate_budget_config()

    def _load_deployment_env(self):
        """Load deployment-specific environment variables"""
        try:
            from dotenv import load_dotenv

            # Try multiple deployment env file locations
            env_paths = [
                Path.cwd() / '.env.deploy',  # Root .env.deploy
                Path.cwd() / 'myapp' / '.env.deploy',  # myapp/.env.deploy
                Path(__file__).parent.parent.parent / '.env.deploy',  # Project root
            ]

            loaded = False
            for env_path in env_paths:
                if env_path.exists():
                    load_dotenv(env_path, override=False)  # Don't override existing vars
                    print(f"✅ Loaded deployment config from {env_path}")
                    loaded = True
                    break

            if not loaded:
                print("ℹ️  No .env.deploy file found, using command line arguments only")
        except ImportError:
            print("ℹ️  python-dotenv not installed, using system environment variables")

    def _apply_env_overrides(self):
        """Override configuration with environment variables"""
        # AWS Configuration
        if os.getenv('AWS_REGION'):
            self.region = os.getenv('AWS_REGION')
        if os.getenv('AWS_FUNCTION_NAME'):
            self.function_name = os.getenv('AWS_FUNCTION_NAME')
        if os.getenv('AWS_ROLE_NAME'):
            self.role_name = os.getenv('AWS_ROLE_NAME')
        if os.getenv('AWS_SCHEDULE_NAME'):
            self.schedule_name = os.getenv('AWS_SCHEDULE_NAME')

        # Budget Configuration
        if os.getenv('MYAPP_BUDGET_EMAIL'):
            self.budget_email = os.getenv('MYAPP_BUDGET_EMAIL')
        if os.getenv('MYAPP_BUDGET_LIMIT'):
            try:
                self.budget_limit = float(os.getenv('MYAPP_BUDGET_LIMIT'))
            except ValueError:
                pass

        # Lambda Configuration
        if os.getenv('LAMBDA_TIMEOUT'):
            try:
                self.timeout = int(os.getenv('LAMBDA_TIMEOUT'))
            except ValueError:
                pass
        if os.getenv('LAMBDA_MEMORY_SIZE'):
            try:
                self.memory_size = int(os.getenv('LAMBDA_MEMORY_SIZE'))
            except ValueError:
                pass
        if os.getenv('LAMBDA_RUNTIME'):
            self.runtime = os.getenv('LAMBDA_RUNTIME')
        if os.getenv('LAMBDA_HANDLER'):
            self.handler = os.getenv('LAMBDA_HANDLER')

        # Schedule Configuration
        if os.getenv('SCHEDULE_EXPRESSION'):
            self.schedule_expression = os.getenv('SCHEDULE_EXPRESSION')

        # Deployment Behavior
        if os.getenv('DEPLOY_DRY_RUN'):
            self.dry_run = os.getenv('DEPLOY_DRY_RUN').lower() in ['true', '1', 'yes']
        if os.getenv('DEPLOY_LOCAL_LAMBDA'):
            self.local_test_enabled = os.getenv('DEPLOY_LOCAL_LAMBDA').lower() in ['true', '1', 'yes']

    def _validate_budget_config(self):
        """Validate budget configuration"""
        if not self.budget_email:
            self.budget_email = os.getenv('MYAPP_BUDGET_EMAIL')

        if not self.budget_email:
            raise ValueError(
                "Budget enforcement requires an email address.\n"
                "Provide it via:\n"
                "  - Command line: --budget-email you@example.com\n"
                "  - Environment: MYAPP_BUDGET_EMAIL=you@example.com\n"
                "  - .env.deploy file: MYAPP_BUDGET_EMAIL=you@example.com\n"
                "  - Or disable budget: --no-budget"
            )