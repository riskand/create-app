# myapp/lambda_function.py
import asyncio
import json
import logging
import os

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


async def myapp_handler():
    """Main Lambda handler function"""
    logger.info("🚀 Starting MyApp - AWS Lambda")

    # Verify required environment variables
    required_vars = ['MYAPP_REQUIRED_VAR']
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        error_msg = f"Missing required environment variables: {missing_vars}"
        logger.error(error_msg)
        raise ValueError(error_msg)

    # Log configuration
    logger.info(f"Configuration loaded from environment")

    # Import after environment checks
    from .service import MyAppService

    # Initialize service - will auto-detect Lambda environment
    service = MyAppService()
    await service.run()

    return {
        'status': 'success',
        'message': 'MyApp completed successfully'
    }


def lambda_handler(event, context):
    """AWS Lambda handler"""
    logger.info(f"Lambda invoked with event: {json.dumps(event)}")

    try:
        result = asyncio.run(myapp_handler())
        logger.info("Lambda execution completed successfully")
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
    except Exception as e:
        logger.error(f"Lambda execution failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            'statusCode': 500,
            'body': json.dumps({
                'status': 'error',
                'message': str(e)
            })
        }