# app/config/__init__.py
# -*- coding: utf-8 -*-
from .schema import CONFIG_SCHEMA
from .manager import ConfigManager

config = ConfigManager(CONFIG_SCHEMA, "data/user_config.json")
