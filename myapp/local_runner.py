# myapp/local_runner.py
import asyncio
import logging
import os
import pathlib
import sys

# Add parent directory to Python path to enable absolute imports
parent_dir = pathlib.Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

# Configure basic logging first for initial messages
loghandler = [logging.StreamHandler(sys.stdout)]
logconfig = {
    "level": logging.INFO,
    "format": '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    "handlers": loghandler
}

logging.basicConfig(**logconfig)
temp_logger = logging.getLogger(__name__)


# Load application environment variables
def load_application_env():
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
                temp_logger.info(f"✅ Loaded application config from {env_path}")
                loaded = True
                break

        if not loaded:
            temp_logger.info("ℹ️  No application .env file found, using system environment")
    except ImportError:
        temp_logger.info("ℹ️  python-dotenv not installed, using system environment variables")


# Load application environment before setting up logging
load_application_env()

# Reconfigure logging with file handler if LOG_DIR is available
log_dir_path = os.getenv('MYAPP_LOG_DIR')
if log_dir_path:
    log_dir = pathlib.Path(log_dir_path)
    log_dir.mkdir(parents=True, exist_ok=True)

    # Remove existing handlers and reconfigure with file handler
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    loghandler.append(logging.FileHandler(log_dir / 'myapp.log'))
    logconfig.update({"handlers": loghandler})
    logging.basicConfig(**logconfig)

logger = logging.getLogger(__name__)


async def main():
    """Local development main function"""
    logger.info("🚀 Starting MyApp - Local Development")

    if log_dir_path:
        logger.info(f"📝 Log file: {pathlib.Path(log_dir_path) / 'myapp.log'}")

    # Check required environment variables
    required_vars = ['MYAPP_REQUIRED_VAR']
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        logger.error(f"❌ Missing required environment variables: {missing_vars}")
        logger.error("Please set them in your .env file or environment")
        return

    logger.info("✅ All required environment variables found")

    try:
        # Use absolute import with the package name
        from myapp.service import MyAppService

        # Initialize service
        service = MyAppService()
        await service.run()

        logger.info("🎉 MyApp completed successfully!")

    except Exception as e:
        logger.error(f"❌ Error running MyApp: {e}")
        import traceback
        logger.error(traceback.format_exc())


if __name__ == "__main__":
    asyncio.run(main())