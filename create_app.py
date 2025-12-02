#!/usr/bin/env python3
# create_app.py
"""
App Generator - Create a new app from the MyApp boilerplate
"""

import os
import re
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Optional


class AppGenerator:
    """Generate a new app from the boilerplate template"""

    def __init__(self, source_dir: str = "."):
        self.source_dir = Path(source_dir).resolve()

        # First, find the boilerplate directory
        self.boilerplate_dir = self._find_boilerplate_dir()
        if not self.boilerplate_dir:
            print("❌ Could not find boilerplate 'myapp' directory")
            print("   Please run this script from a directory containing 'myapp/'")
            sys.exit(1)

        # Find root files (deploy.py, README.md, requirements.txt)
        self.root_files = self._find_root_files()

    def _find_boilerplate_dir(self) -> Optional[Path]:
        """Find the myapp boilerplate directory"""
        # Check if we're inside a myapp directory
        if self.source_dir.name == "myapp":
            if (self.source_dir / "__init__.py").exists():
                # This is the package itself
                return self.source_dir
            elif (self.source_dir / "myapp" / "__init__.py").exists():
                # This is a directory containing the package
                return self.source_dir

        # Check current directory for myapp/
        if (self.source_dir / "myapp").exists():
            test_dir = self.source_dir / "myapp"
            if (test_dir / "__init__.py").exists() or (test_dir / "myapp" / "__init__.py").exists():
                return test_dir

        # Check current directory for myapp package directly
        if (self.source_dir / "__init__.py").exists():
            # Check if this looks like the myapp package by checking for service.py
            if (self.source_dir / "service.py").exists():
                return self.source_dir

        # Check one level up
        parent_dir = self.source_dir.parent
        if (parent_dir / "myapp").exists():
            test_dir = parent_dir / "myapp"
            if (test_dir / "__init__.py").exists() or (test_dir / "myapp" / "__init__.py").exists():
                return test_dir

        return None

    def _find_root_files(self) -> Dict[str, Path]:
        """Find deployment root files"""
        root_files = {}

        # Files to look for
        target_files = ["deploy.py", "README.md", "requirements.txt"]

        for file_name in target_files:
            # Check in current directory
            file_path = self.source_dir / file_name
            if file_path.exists():
                root_files[file_name] = file_path
                continue

            # Check in boilerplate directory
            file_path = self.boilerplate_dir / file_name
            if file_path.exists():
                root_files[file_name] = file_path
                continue

            # Check in parent of boilerplate directory
            file_path = self.boilerplate_dir.parent / file_name
            if file_path.exists():
                root_files[file_name] = file_path

        return root_files

    def validate_boilerplate(self) -> bool:
        """Check if boilerplate exists and has required structure"""
        print(f"🔍 Found boilerplate at: {self.boilerplate_dir}")

        # Determine the package directory
        if (self.boilerplate_dir / "myapp" / "__init__.py").exists():
            # Structure: myapp/myapp/__init__.py
            self.package_source = self.boilerplate_dir / "myapp"
            print(f"📁 Package source: {self.package_source}")
        elif (self.boilerplate_dir / "__init__.py").exists():
            # Structure: myapp/__init__.py (boilerplate_dir is the package)
            self.package_source = self.boilerplate_dir
            print(f"📁 Package source: {self.package_source} (direct)")
        else:
            print("❌ Cannot find myapp package structure")
            print(f"   Looked for __init__.py in {self.boilerplate_dir} and {self.boilerplate_dir / 'myapp'}")
            return False

        # Check for required package files
        required_package_files = [
            self.package_source / "__init__.py",
            self.package_source / "service.py",
            self.package_source / "deployer" / "deployer.py",
        ]

        missing_files = []
        for req_file in required_package_files:
            if not req_file.exists():
                missing_files.append(str(req_file.relative_to(self.boilerplate_dir)))

        if missing_files:
            print("❌ Missing boilerplate package files:")
            for f in missing_files:
                print(f"   - {f}")
            return False

        # Check for root files
        print("\n📋 Found deployment files:")
        for name, path in self.root_files.items():
            print(f"   ✅ {name}: {path.relative_to(self.source_dir) if path.is_relative_to(self.source_dir) else path}")

        # Warn about missing recommended files but don't fail
        recommended_files = ["deploy.py", "README.md"]
        missing_recommended = [f for f in recommended_files if f not in self.root_files]
        if missing_recommended:
            print(f"\n⚠️  Missing recommended files: {missing_recommended}")
            print("   You can add them manually after app creation")

        return True

    def get_user_input(self) -> Dict[str, str]:
        """Get app configuration from user"""
        print("\n" + "=" * 60)
        print("🛠️  App Configuration Generator")
        print("=" * 60)

        # Get app name
        while True:
            app_name = input("\n📝 Enter your app name (lowercase, letters, numbers and underscores only): ").strip()
            if not app_name:
                print("❌ App name cannot be empty")
                continue

            # Validate app name
            if not re.match(r'^[a-z][a-z0-9_]*$', app_name):
                print("❌ Invalid app name. Use lowercase letters, numbers, and underscores only.")
                print("   Examples: 'data_processor', 'email_service', 'report_generator'")
                continue

            # Check for reserved names
            reserved_names = ['app', 'application', 'lambda', 'aws', 'test']
            if app_name in reserved_names:
                print(f"❌ '{app_name}' is a reserved name. Please choose a different name.")
                continue

            break

        # Get display name
        display_name = input(f"📝 Enter display name for {app_name} (e.g., 'My Awesome App'): ").strip()
        if not display_name:
            display_name = app_name.replace("_", " ").title()

        # Get description
        description = input(f"📝 Enter description for {display_name}: ").strip()
        if not description:
            description = f"{display_name} - AWS Lambda Application"

        # Get target directory
        default_target = str(self.source_dir.parent / app_name)
        target_dir = input(f"📁 Enter target directory [{default_target}]: ").strip()
        if not target_dir:
            target_dir = default_target

        # Get author/contact info
        author = input(f"👤 Enter author name (optional): ").strip()
        contact = input(f"📧 Enter contact email (optional): ").strip()

        return {
            "app_name": app_name,
            "app_name_camel": ''.join(word.title() for word in app_name.split('_')),
            "app_name_pascal": ''.join(word.title() for word in app_name.split('_')),
            "app_name_upper": app_name.upper(),
            "app_name_lower": app_name.lower(),
            "display_name": display_name,
            "description": description,
            "target_dir": target_dir,
            "author": author,
            "contact": contact,
        }

    def replace_content(self, content: str, config: Dict[str, str]) -> str:
        """Replace template variables in content"""
        # Basic replacements
        replacements = {
            "MyApp": config["app_name_pascal"],
            "My App": config["display_name"],
            "MYAPP": config["app_name_upper"],
            "myapp": config["app_name_lower"],
            "[Your app description]": config["description"],
            "MyApp Budget": f"{config['display_name']} Budget",
            "myapp-lambda-role": f"{config['app_name_lower']}-lambda-role",
            "myapp-schedule": f"{config['app_name_lower']}-schedule",
            "'myapp'": f"'{config['app_name_lower']}'",
            '"myapp"': f'"{config["app_name_lower"]}"',
        }

        result = content
        for old, new in replacements.items():
            result = result.replace(old, new)

        return result

    def copy_and_transform(self, config: Dict[str, str]) -> bool:
        """Copy boilerplate and transform files"""
        target_dir = Path(config["target_dir"]).resolve()
        app_dir = target_dir / config["app_name_lower"]

        # Check if target exists
        if target_dir.exists():
            print(f"\n⚠️  Directory '{target_dir}' already exists.")
            print("   Contents will be overwritten!")
            response = input("   Continue? (y/N): ").strip().lower()
            if response not in ['y', 'yes']:
                print("❌ Operation cancelled")
                return False

        print(f"\n📦 Creating new app: {config['display_name']}")
        print(f"📁 Target directory: {target_dir}")

        try:
            # Create directory structure
            target_dir.mkdir(parents=True, exist_ok=True)
            app_dir.mkdir(parents=True, exist_ok=True)
            (app_dir / "deployer").mkdir(parents=True, exist_ok=True)

            # Copy and transform files
            self._copy_files(app_dir, config)

            # Create example environment files
            self.create_env_examples(app_dir, config)

            # Update requirements.txt with proper indentation
            self._update_requirements(app_dir, config)

            print(f"\n✅ Successfully created '{config['display_name']}' at {target_dir}")

            return True

        except Exception as e:
            print(f"❌ Error creating app: {e}")
            import traceback
            traceback.print_exc()

            # Clean up on error
            if target_dir.exists():
                response = input(
                    f"\n⚠️  Error occurred. Remove created directory '{target_dir}'? (y/N): ").strip().lower()
                if response in ['y', 'yes']:
                    shutil.rmtree(target_dir)
                    print(f"🗑️  Removed {target_dir}")
            return False

    def _copy_files(self, app_dir: Path, config: Dict[str, str]) -> None:
        """Copy and transform individual files"""

        # Copy root files (deploy.py, requirements.txt, README.md)
        print("\n📦 Copying deployment files:")
        for file_name, source_file in self.root_files.items():
            if file_name == "requirements.txt":
                # Skip requirements.txt for now, we'll create it specially
                continue

            target_file = app_dir.parent / file_name
            self._transform_file(source_file, target_file, config)
            print(f"   📄 Created: {target_file.name}")

        print("\n📦 Copying package files:")
        # Copy app package files
        self._copy_package_files(self.package_source, app_dir, config)

    def _copy_package_files(self, source_dir: Path, target_dir: Path, config: Dict[str, str]) -> None:
        """Copy package files recursively"""
        for item in source_dir.iterdir():
            if item.is_file():
                if item.name in ["__pycache__", ".pyc", ".pyo"] or item.suffix == ".pyc" or item.name.startswith("."):
                    continue

                # Skip files we handle specially
                if item.name in ["requirements.txt", "README.md", "deploy.py"]:
                    continue

                target_file = target_dir / item.name
                self._transform_file(item, target_file, config)
                print(f"   📄 Created: {target_file.relative_to(target_dir.parent)}")
            elif item.is_dir():
                if item.name in ["__pycache__", ".git", ".venv", "venv", "node_modules", ".idea", ".vscode"]:
                    continue

                if item.name.startswith("."):
                    continue

                # Create subdirectory
                sub_target = target_dir / item.name
                sub_target.mkdir(parents=True, exist_ok=True)

                # Handle deployer directory specially
                if item.name == "deployer":
                    # Ensure deployer has __init__.py
                    deployer_init = sub_target / "__init__.py"
                    if not deployer_init.exists():
                        deployer_init.write_text(f'"""{config["display_name"]} Deployment Module"""\n\n')

                    # Copy deployer files
                    for deployer_item in item.iterdir():
                        if deployer_item.is_file() and not deployer_item.name.startswith("."):
                            target_file = sub_target / deployer_item.name
                            self._transform_file(deployer_item, target_file, config)
                            print(f"   📄 Created: {target_file.relative_to(target_dir.parent)}")
                else:
                    # Recursively copy other directories
                    self._copy_package_files(item, sub_target, config)

    def _transform_file(self, source: Path, target: Path, config: Dict[str, str]) -> None:
        """Read, transform, and write a file"""
        try:
            content = source.read_text(encoding='utf-8')
            transformed = self.replace_content(content, config)
            target.write_text(transformed, encoding='utf-8')

            # Make deploy.py executable
            if target.name == "deploy.py":
                os.chmod(target, 0o755)

        except UnicodeDecodeError:
            # If it's not a text file, copy it binary
            shutil.copy2(source, target)

    def _update_requirements(self, app_dir: Path, config: Dict[str, str]) -> None:
        """Update requirements.txt with proper app name"""
        requirements_file = app_dir.parent / "requirements.txt"

        if not requirements_file.exists():
            # Create a basic requirements.txt
            requirements_content = f"""# {config['display_name']} - Dependencies
# Application dependencies
python-dotenv==1.0.0    # Environment variable management

# AWS dependencies (for Lambda execution and deployment)
boto3==1.34.0           # AWS SDK for Python
botocore==1.34.0        # AWS core library

# Deployment tool (from private GitLab)
# Note: Requires GITLAB_TOKEN environment variable for installation
lambda-deploy-tool @ git+https://oauth2:${{GITLAB_TOKEN}}@gitlab.com/luona-common-libraries/lambda-deploy-tool.git@main

# Add your application-specific dependencies here
# Example: requests==2.31.0
# Example: pandas==2.0.3
"""
            requirements_file.write_text(requirements_content)
            print(f"   📄 Created: {requirements_file.name}")

    def create_env_examples(self, app_dir: Path, config: Dict[str, str]) -> None:
        """Create example environment files"""
        print("\n📝 Creating environment files:")

        # Create .env.example
        env_example = app_dir / ".env.example"
        env_content = f"""# {config['display_name']} Configuration
# Copy this file to .env and fill in the values

# Required variables
{config['app_name_upper']}_REQUIRED_VAR=your_value_here
{config['app_name_upper']}_SETTING=default_value

# Optional variables
{config['app_name_upper']}_LOG_DIR=/tmp/{config['app_name_lower']}

# Feature flags (prefix with {config['app_name_upper']}_FEATURE_)
# {config['app_name_upper']}_FEATURE_EXAMPLE=true
# {config['app_name_upper']}_FEATURE_NEWUI=false
"""
        env_example.write_text(env_content)
        print(f"   📄 Created: {env_example.relative_to(app_dir.parent)}")

        # Create .env.deploy.example
        deploy_env_example = app_dir.parent / ".env.deploy.example"
        deploy_env_content = f"""# {config['display_name']} Deployment Configuration
# Copy this file to .env.deploy and fill in the values

# AWS Configuration
AWS_REGION=ap-southeast-1
AWS_FUNCTION_NAME={config['app_name_lower']}
AWS_ROLE_NAME={config['app_name_lower']}-lambda-role
AWS_SCHEDULE_NAME={config['app_name_lower']}-schedule

# Budget Configuration
{config['app_name_upper']}_BUDGET_EMAIL=your-email@example.com
{config['app_name_upper']}_BUDGET_LIMIT=10

# Lambda Configuration
LAMBDA_TIMEOUT=300
LAMBDA_MEMORY_SIZE=256
LAMBDA_RUNTIME=python3.11
LAMBDA_HANDLER={config['app_name_lower']}.lambda_function.lambda_handler

# Schedule Configuration
SCHEDULE_EXPRESSION=rate(1 hour)

# Deployment Behavior
DEPLOY_DRY_RUN=false
DEPLOY_LOCAL_LAMBDA=false
"""
        deploy_env_example.write_text(deploy_env_content)
        print(f"   📄 Created: {deploy_env_example.name}")

        # Create .gitignore
        gitignore_file = app_dir.parent / ".gitignore"
        gitignore_content = f"""# {config['display_name']} - Git Ignore

# Environment files
.env
.env.deploy
.env.local
.env.*.local

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
.venv/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Local test files
local-test*.json
"""
        gitignore_file.write_text(gitignore_content)
        print(f"   📄 Created: {gitignore_file.name}")

    def show_next_steps(self, config: Dict[str, str]) -> None:
        """Display next steps for the user"""
        print("\n" + "=" * 60)
        print("🚀 Next Steps:")
        print("=" * 60)
        print(f"1. Navigate to your app directory:")
        print(f"   cd {config['target_dir']}")
        print(f"\n2. Set up your environment:")
        print(f"   cp {config['app_name_lower']}/.env.example {config['app_name_lower']}/.env")
        print(f"   cp .env.deploy.example .env.deploy")
        print(f"   # Edit these files with your actual values")
        print(f"\n3. Set up virtual environment:")
        print(f"   python -m venv venv")
        print(f"   source venv/bin/activate  # On Windows: venv\\Scripts\\activate")
        print(f"\n4. Install dependencies:")
        print(f"   pip install -r requirements.txt")
        print(f"   # Set GITLAB_TOKEN if using private dependencies:")
        print(f"   # export GITLAB_TOKEN=your_token_here")
        print(f"\n5. Run locally to test:")
        print(f"   python -m {config['app_name_lower']}.local_runner")
        print(f"\n6. Deploy to AWS (when ready):")
        print(f"   python deploy.py --dry-run  # Test first")
        print(f"   python deploy.py            # Deploy for real")
        print(f"\n7. Check the README.md for more details!")


def main():
    """Main function"""
    print("=" * 60)
    print("🛠️  AWS Lambda App Generator")
    print("=" * 60)
    print("This script will create a new app from the MyApp boilerplate.")
    print("Make sure you have the boilerplate files in the current directory.")

    generator = AppGenerator()

    # Validate boilerplate exists
    if not generator.validate_boilerplate():
        print("\n❌ Boilerplate validation failed.")
        print("Please ensure you have the MyApp boilerplate files available.")
        print("\nExpected structure:")
        print("  myapp/                 # The boilerplate directory")
        print("  ├── myapp/             # The package (or myapp/ itself is the package)")
        print("  │   ├── __init__.py")
        print("  │   ├── service.py")
        print("  │   └── deployer/")
        print("  ├── deploy.py          # Optional but recommended")
        print("  └── README.md          # Optional but recommended")
        sys.exit(1)

    # Get user input
    config = generator.get_user_input()

    # Confirm creation
    print("\n" + "=" * 60)
    print("📋 Configuration Summary:")
    print("=" * 60)
    print(f"  App Name: {config['app_name_lower']}")
    print(f"  Display Name: {config['display_name']}")
    print(f"  Description: {config['description']}")
    print(f"  Target Directory: {config['target_dir']}")
    if config['author']:
        print(f"  Author: {config['author']}")
    if config['contact']:
        print(f"  Contact: {config['contact']}")

    confirm = input("\n✅ Create this app? (Y/n): ").strip().lower()
    if confirm in ['n', 'no']:
        print("❌ Operation cancelled")
        sys.exit(0)

    # Create the app
    if generator.copy_and_transform(config):
        generator.show_next_steps(config)
        print("\n🎉 App creation complete! Happy coding! 🚀")
    else:
        print("\n❌ Failed to create app")
        sys.exit(1)


if __name__ == "__main__":
    main()