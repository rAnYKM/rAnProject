# -*- coding: utf-8 -*-
#
# Copyright 2016 rAnYKM (Jiayi Chen)
#

""" settings.py - rAnProject Configuration Module Python

Define Constants

"""

import os

# Module Names
SNAP_DATA_MODULE = 'SNAPdata'
ATTACK_MODULE = 'rAnAttack'
PROTECTION_MODULE = 'rAnPriv'
DEMO_MODULE = 'rAnPage'

# SNAP_DATA_MODULE
GOOGLE_PLUS = 'GooglePlus'
FACEBOOK = 'Facebook'

# ATTACK_MODULE

# PROTECTION_MODULE

# DEMO_MODULE

# Directory Constants Definition
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_DIR = os.path.join(ROOT_DIR, 'settings.ini')
GOOGLE_EGO_NODE_LIST_DIR = os.path.join(ROOT_DIR, SNAP_DATA_MODULE, GOOGLE_PLUS, 'nodeList.txt')
FACEBOOK_EGO_NODE_LIST_DIR = os.path.join(ROOT_DIR, SNAP_DATA_MODULE, FACEBOOK, 'nodeList.txt')
