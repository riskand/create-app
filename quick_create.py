#!/usr/bin/env python3
# quick_create.py
"""
Quick app creator - Simple version with fewer prompts
"""

import os
import re
import shutil
import sys
from pathlib import Path


def create_app(app_name: str, target_dir: str = None, description: str = None):
    """Quickly create a new app"""

    # Validate app name
    if not re.match(r'^[a-z][a-z0-9_]*$', app_name):
        print(f"❌ Invalid app name: {app_name}")
        print("   Use lowercase letters, numbers, and underscores only.")
        sys.exit(1)

    # Set default target directory
    if not target_dir:
        target_dir = str(Path.cwd().parent / app_name)

    # Set default description
    if not description:
        description = f"{app_name.replace('_', ' ').title()} - AWS Lambda Application"

    # Configuration
    config = {
        "app_name": app_name,
        "app_name_camel": ''.join(word.title() for word in app_name.split('_')),
        "app_name_pascal": ''.join(word.title() for word in app_name.split('_')),
        "app_name_upper": app_name.upper(),
        "app_name_lower": app_name.lower(),
        "display_name": app_name.replace('_', ' ').title(),
        "description": description,
        "target_dir": target_dir,
    }

    print(f"📦 Creating app: {config['display_name']}")
    print(f"📁 Target: {target_dir}")

    # Find boilerplate (simplified logic)
    boilerplate_dir = Path("myapp")
    if not boilerplate_dir.exists():
        print("❌ Could not find 'myapp' directory")
        print("   Run this from the directory containing the MyApp boilerplate")
        sys.exit(1)

    # Determine package source
    if (boilerplate_dir / "myapp" / "__init__.py").exists():
        package_source = boilerplate_dir / "myapp"
    elif (boilerplate_dir / "__init__.py").exists():
        package_source = boilerplate_dir
    else:
        print("❌ Invalid boilerplate structure")
        sys.exit(1)

    # Create target directories
    target_path = Path(target_dir)
    app_dir = target_path / config["app_name_lower"]

    if target_path.exists():
        print(f"⚠️  Directory exists: {target_dir}")
        response = input("   Overwrite? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("❌ Cancelled")
            sys.exit(0)
        # Remove existing directory
        shutil.rmtree(target_path)

    target_path.mkdir(parents=True, exist_ok=True)
    app_dir.mkdir(parents=True, exist_ok=True)
    (app_dir / "deployer").mkdir(parents=True, exist_ok=True)

    # Replacement function
    def replace_content(content: str) -> str:
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

    # Copy and transform files
    print("\n📦 Copying files...")

    # Copy package files
    def copy_tree(src: Path, dst: Path):
        for item in src.iterdir():
            if item.name in ["__pycache__", ".pyc", ".git"] or item.name.startswith("."):
                continue

            if item.is_file():
                if item.suffix == ".pyc":
                    continue

                # Read, transform, write
                content = item.read_text(encoding='utf-8')
                transformed = replace_content(content)
                target_file = dst / item.name
                target_file.write_text(transformed, encoding='utf-8')

                # Make deploy.py executable
                if target_file.name == "deploy.py":
                    os.chmod(target_file, 0o755)

            elif item.is_dir():
                sub_dst = dst / item.name
                sub_dst.mkdir(exist_ok=True)
                copy_tree(item, sub_dst)

    # Copy main package
    copy_tree(package_source, app_dir)

    # Create deployer __init__.py if missing
    deployer_init = app_dir / "deployer" / "__init__.py"
    if not deployer_init.exists():
        deployer_init.write_text(f'"""{config["display_name"]} Deployment Module"""\n')

    # Copy root files if they exist
    for root_file in ["deploy.py", "README.md", "requirements.txt"]:
        source_file = Path(root_file)
        if source_file.exists():
            content = source_file.read_text(encoding='utf-8')
            transformed = replace_content(content)
            target_file = target_path / root_file
            target_file.write_text(transformed, encoding='utf-8')

    # Create basic files
    print("📝 Creating environment files...")

    # .env.example
    env_example = app_dir / ".env.example"
    env_example.write_text(f"""# {config['display_name']} Configuration
{config['app_name_upper']}_REQUIRED_VAR=your_value_here
{config['app_name_upper']}_SETTING=default_value
""")

    # .env.deploy.example
    deploy_env = target_path / ".env.deploy.example"
    deploy_env.write_text(f"""# {config['display_name']} Deployment
AWS_REGION=ap-southeast-1
AWS_FUNCTION_NAME={config['app_name_lower']}
{config['app_name_upper']}_BUDGET_EMAIL=your-email@example.com
""")

    # .gitignore
    gitignore = target_path / ".gitignore"
    gitignore.write_text(f"""# {config['display_name']}
.env
.env.deploy
__pycache__/
*.pyc
venv/
""")

    print(f"\n✅ Created '{config['display_name']}' at {target_dir}")
    print(f"\n🚀 Quick start:")
    print(f"   cd {target_dir}")
    print(f"   cp {config['app_name_lower']}/.env.example {config['app_name_lower']}/.env")
    print(f"   cp .env.deploy.example .env.deploy")
    print(f"   # Edit .env and .env.deploy with your values")
    print(f"   python -m {config['app_name_lower']}.local_runner")
    print(f"\n🎉 Done!")


def main():
    """Main function with command line arguments"""
    import argparse

    parser = argparse.ArgumentParser(description="Quickly create a new app from boilerplate")
    parser.add_argument("app_name", help="App name (lowercase with underscores)")
    parser.add_argument("-d", "--dir", help="Target directory (default: ../app_name)")
    parser.add_argument("--desc", help="App description")

    args = parser.parse_args()

    create_app(args.app_name, args.dir, args.desc)


if __name__ == "__main__":
    main()