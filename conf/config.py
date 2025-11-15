# -*- coding: utf-8 -*-
"""Configuration module for Coke Agent."""

import json
import os

# Get the directory where this config.py file is located
CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

# Load configuration from JSON file
with open(CONFIG_FILE, "r", encoding="utf-8") as f:
    CONF = json.load(f)

# Export CONF as the main configuration object
__all__ = ["CONF"]
