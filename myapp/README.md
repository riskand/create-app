# MyApp

[Brief description of what your application does]

## Features

- Feature 1
- Feature 2
- Feature 3

## Prerequisites

- Python 3.11+
- AWS Account with appropriate permissions
- AWS CLI configured with credentials
- GitLab access token (for private dependencies)

## Project Structure

```
myapp/
├── myapp/                      # Main application package
│   ├── __init__.py
│   ├── config.py              # Application configuration
│   ├── service.py             # Main service logic
│   ├── lambda_function.py     # AWS Lambda entry point
│   └── local_runner.py        # Local development runner
│
├── myapp/deployer/            # Deployment package
│   ├── __init__.py
│   ├── deployer.py           # Deployment script
│   ├── config.py             # Deployment configuration
│   └── validators.py         # Environment validators
│
├── deploy.py                  # Deployment entry point
├── requirements.txt           # Dependencies
└── README.md                 # This file
```

## Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd myapp
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

Set your GitLab token as an environment variable:

```bash
export GITLAB_TOKEN=your_gitlab_token_here
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### 4. Configure Application

Copy the example environment file:

```bash
cp myapp/.env.example myapp/.env
```

Edit `myapp/.env` and fill in your configuration values.

### 5. Configure Deployment

Copy the deployment environment file:

```bash
cp .env.deploy.example .env.deploy
```

Edit `.env.deploy` and fill in your AWS and deployment configuration.

## Local Development

Run the application locally:

```bash
python -m myapp.local_runner
```

This will:
- Load configuration from `myapp/.env`
- Run the application logic locally
- Output logs to console and file (if configured)

## Deployment

### Deploy to AWS Lambda

```bash
python deploy.py
```

This will:
1. Validate your environment configuration
2. Build the Lambda deployment package
3. Create/update IAM roles and policies
4. Deploy the Lambda function
5. Set up EventBridge schedule
6. Configure budget alerts (if enabled)

### Deployment Options

```bash
# Dry run (preview without making changes)
python deploy.py --dry-run

# Build package only (no deployment)
python deploy.py --build-only

# Skip validation
python deploy.py --skip-validation

# Verbose output
python deploy.py --verbose

# Custom configuration
python deploy.py \
  --region us-west-2 \
  --function-name myapp-prod \
  --budget-email alerts@example.com \
  --budget-limit 20
```

### Local Lambda Testing

Test the Lambda function locally without deploying:

```bash
python deploy.py --local-lambda
```

## Environment Variables

### Application Variables (myapp/.env)

| Variable | Required | Description |
|----------|----------|-------------|
| `MYAPP_REQUIRED_VAR` | Yes | Description |
| `MYAPP_SETTING` | Yes | Description |
| `MYAPP_LOG_DIR` | No | Log directory (default: /tmp/myapp) |
| `MYAPP_FEATURE_*` | No | Feature flags |

### Deployment Variables (.env.deploy)

| Variable | Required | Description |
|----------|----------|-------------|
| `AWS_REGION` | No | AWS region (default: ap-southeast-1) |
| `MYAPP_BUDGET_EMAIL` | Yes* | Email for budget alerts (*if budget enabled) |
| `MYAPP_BUDGET_LIMIT` | No | Monthly budget in USD (default: 10) |
| `LAMBDA_TIMEOUT` | No | Function timeout in seconds (default: 300) |
| `LAMBDA_MEMORY_SIZE` | No | Function memory in MB (default: 256) |
| `SCHEDULE_EXPRESSION` | No | EventBridge schedule (default: rate(1 hour)) |

## Schedule Configuration

The Lambda function runs on a schedule defined by `SCHEDULE_EXPRESSION`.

Examples:
- `rate(1 hour)` - Every hour
- `rate(30 minutes)` - Every 30 minutes
- `cron(0 12 * * ? *)` - Every day at 12:00 UTC
- `cron(0/15 1-14 ? * * *)` - Every 15 minutes from 08:00-21:00 GMT+7

## Monitoring

### CloudWatch Logs

View Lambda execution logs:

```bash
aws logs tail /aws/lambda/myapp --follow
```

### Budget Alerts

After deployment, check your email for SNS subscription confirmation. You'll receive alerts when:
- Actual costs exceed 80% of budget
- Forecasted costs exceed 100% of budget

## Troubleshooting

### Common Issues

**Issue: Missing dependencies**
```bash
# Solution: Reinstall with GitLab token
export GITLAB_TOKEN=your_token
pip install -r requirements.txt --force-reinstall
```

**Issue: Authentication errors**
```bash
# Solution: Check AWS credentials
aws sts get-caller-identity
```

**Issue: Deployment validation fails**
```bash
# Solution: Verify environment variables
cat myapp/.env
python deploy.py --verbose
```

## Development

### Adding New Features

1. Create new modules in `myapp/` directory
2. Update `myapp/service.py` to integrate new functionality
3. Add any new dependencies to `requirements.txt`
4. Update environment variable examples if needed
5. Test locally with `python -m myapp.local_runner`
6. Deploy with `python deploy.py`

### Code Style

Follow PEP 8 guidelines and maintain:
- Single Responsibility Principle (SRP) for classes
- Clear separation of concerns
- Comprehensive logging
- Error handling

## License

[Your license here]

## Contributing

[Contributing guidelines here]

## Contact

[Your contact information here]
