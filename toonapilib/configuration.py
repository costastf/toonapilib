#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# File: configuration.py
"""A place to store the configuration."""


STATE_CACHING_SECONDS = 300

STATES = {0: 'Comfort',
          1: 'Home',
          2: 'Sleep',
          3: 'Away',
          4: 'Holiday',
          5: 'Unknown'}

BURNER_STATES = {0: 'off',
                 1: 'on',
                 2: 'water_heating',
                 3: 'pre_heating'}

PROGRAM_STATES = {0: 'off',
                  1: 'on',
                  2: 'manual'}
