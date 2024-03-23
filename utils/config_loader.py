# -*- coding: utf-8 -*-
"""
Created on Fri Mar 22 11:56:48 2024

@author: rubir
"""

import json

def load_config(config_path):
    with open(config_path, 'r') as f:
        return json.load(f)
