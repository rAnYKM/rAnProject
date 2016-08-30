# -*- coding: utf-8 -*-
#
# Copyright 2016 rAnYKM (Jiayi Chen)
#

""" ranfig.py - rAnProject Configuration Module

Load the basic settings for rAnProject

"""

import ConfigParser as cp

DEFAULT_SETTING_FILE = '../settings.ini'


def load_ranfig(file=DEFAULT_SETTING_FILE):
    config = cp.ConfigParser()
    config.read(file)
    ranfig = {section: {option: config.get(section, option)
                        for option in config.options(section)}
              for section in config.sections()}
    return ranfig

if __name__ == '__main__':
    print load_ranfig()
