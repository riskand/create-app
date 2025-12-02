#!/usr/bin/env python3
# myapp/deploy.py
"""
Deploy MyApp
"""
import sys
from myapp.deployer.deployer import main

if __name__ == '__main__':
    sys.exit(main())