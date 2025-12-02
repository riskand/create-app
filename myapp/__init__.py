# myapp/__init__.py
"""
MyApp - [Your app description]
AWS Lambda compatible modular package
"""

__version__ = "1.0.0"

from .service import MyAppService
from .config import Config

__all__ = [
    'MyAppService',
    'Config',
]
