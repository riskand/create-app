# myapp/deployer/deployer.py
"""
Single entry point for MyApp deployment using generic deployment system
"""
import logging
import os
import sys
import traceback
from pathlib import Path

# Configure logging first for initial messages
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Import generic deployment system
from lambda_deploy_tool.args import DeploymentArgumentParser
from lambda_deploy_tool.deployer import Deployer

# Import MyApp specific components from same directory
from .config import MyAppDeployConfig
from .validators import MyAppEnvironmentValidator, MyAppConfigValidator


class MyAppDeploymentError(Exception):
    """Custom exception for MyApp deployment errors"""
    pass


def create_myapp_argument_parser() -> DeploymentArgumentParser:
    """Create argument parser for MyApp"""
    parser = DeploymentArgumentParser(
        script_name='myapp_deployer.py',
        description='Deploy MyApp to AWS Lambda'
    )

    # Customize defaults for MyApp
    parser.parser.set_defaults(
        function_name='myapp',
        budget_name='MyApp Budget'
    )

    # Add MyApp-specific arguments if needed
    myapp_group = parser.add_argument_group('MyApp Options')
    myapp_group.add_argument(
        '--custom-option',
        action='store_true',
        help='Custom option for MyApp'
    )

    return parser


def get_myapp_deployment_steps(deployer, config, args) -> list:
    """Get MyApp-specific deployment steps"""
    # Get default steps from generic deployer
    steps = deployer.get_default_deployment_steps()

    # Add custom steps if needed
    # Example: Insert custom step after IAM setup
    # for i, (step_name, _) in enumerate(steps):
    #     if step_name == "IAM Setup":
    #         insert_position = i + 1
    #         steps.insert(insert_position, ("Custom Step", lambda: custom_function()))
    #         break

    return steps


def main() -> int:
    """Main MyApp deployment function"""
    parser = create_myapp_argument_parser()
    args = parser.parse_args()

    try:
        # Set log level
        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)

        logger.info("🚀 MyApp Deployment")
        logger.info("=" * 60)

        # Step 1: Load application environment for validation
        logger.info("\n📋 Step 1: Loading Application Configuration")
        logger.info("-" * 60)

        # Load application .env for validation
        try:
            from dotenv import load_dotenv

            # Try multiple locations for application .env
            app_env_paths = [
                Path.cwd() / 'myapp' / '.env',  # myapp/.env
                Path.cwd() / '.env',  # Root .env
            ]

            app_env_loaded = False
            for env_path in app_env_paths:
                if env_path.exists():
                    load_dotenv(env_path, override=True)
                    logger.info(f"✅ Loaded application config from {env_path}")
                    app_env_loaded = True
                    break

            if not app_env_loaded:
                logger.warning("⚠️  No application .env file found")
                logger.info("💡 Create one from .env.example:")
                logger.info("   cp myapp/.env.example myapp/.env")
        except ImportError:
            logger.info("ℹ️  python-dotenv not installed, using system environment")

        # Step 2: MyApp-specific validation
        if not args.skip_validation:
            logger.info("\n📋 Step 2: MyApp Environment Validation")
            logger.info("-" * 60)

            env_validator = MyAppEnvironmentValidator()
            if not env_validator.validate():
                raise MyAppDeploymentError("Environment validation failed")

            config_validator = MyAppConfigValidator()
            if not config_validator.validate():
                raise MyAppDeploymentError("Configuration validation failed")

            logger.info("✅ MyApp environment validation passed")
        else:
            logger.warning("⚠️  Skipping validation (--skip-validation)")

        # Step 3: Load MyApp configuration (will load .env.deploy automatically)
        logger.info("\n⚙️  Step 3: Loading Deployment Configuration")
        logger.info("-" * 60)

        config = MyAppDeployConfig(
            source_dir=args.source_dir,
            output_dir=args.output_dir,
            region=args.region,
            function_name=args.function_name,
            budget_limit=args.budget_limit,
            budget_email=args.budget_email,
            budget_name=args.budget_name,
            enable_budget=not args.no_budget,
            dry_run=args.dry_run,
            local_test_enabled=args.local_lambda
        )

        # Log configuration summary
        logger.info(f"📋 Configuration Summary:")
        logger.info(f"  Function: {config.function_name}")
        logger.info(f"  Region: {config.region}")
        logger.info(f"  Runtime: {config.runtime}")
        logger.info(f"  Memory: {config.memory_size} MB")
        logger.info(f"  Timeout: {config.timeout} sec")
        logger.info(f"  Schedule: {config.schedule_expression}")

        if config.local_test_enabled:
            logger.info("  Mode: 🧪 LOCAL TEST ONLY")
        elif config.enable_budget:
            logger.info(f"  Budget: 💰 ${config.budget_limit}/month")
            logger.info(f"  Budget Name: {config.budget_name}")
            if config.budget_email:
                logger.info(f"  Alert Email: {config.budget_email}")
        else:
            logger.warning("  Budget: ⚠️ DISABLED (not recommended)")

        # Step 4: Deploy using generic deployment system
        logger.info("\n🚀 Step 4: Deployment")
        logger.info("-" * 60)

        deployer = Deployer(config)

        # Set custom MyApp deployment steps
        deployment_steps = get_myapp_deployment_steps(deployer, config, args)
        deployer.set_deployment_steps(deployment_steps)

        if args.build_only:
            logger.info("📦 Building Lambda package only (--build-only)")
            package_path = deployer.build()
            logger.info(f"✅ Package built: {package_path}")

            # Show build summary
            logger.info("\n" + "=" * 60)
            logger.info("🎉 BUILD COMPLETE!")
            logger.info("=" * 60)
            logger.info(f"📦 Package: {package_path}")
            logger.info(f"📂 Output Dir: {config.output_dir}")
        else:
            deployer.deploy()

            # Show MyApp-specific reminders
            if not config.local_test_enabled and not config.dry_run:
                logger.info("\n📝 MyApp Specific Notes:")
                logger.info("-" * 60)
                logger.info("📧 Budget Email: Check your inbox for SNS subscription confirmation")
                logger.info(f"⏰ Schedule: {config.schedule_expression}")

        return 0

    except KeyboardInterrupt:
        logger.warning("\n⚠️  Deployment interrupted by user")
        return 130
    except MyAppDeploymentError as e:
        logger.error(f"\n❌ MyApp deployment failed: {e}")
        return 1
    except Exception as e:
        logger.error(f"\n❌ Unexpected error: {e}")
        if args.verbose:
            logger.error(f"Traceback: {traceback.format_exc()}")
        return 1


if __name__ == '__main__':
    sys.exit(main())