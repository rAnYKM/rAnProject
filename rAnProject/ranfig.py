# -*- coding: utf-8 -*-
#
# Copyright 2016 rAnYKM (Jiayi Chen)
#

""" ranfig.py - rAnProject Configuration Module

Load the basic settings for rAnProject

"""

import ConfigParser as cp
import rAnProject.settings as settings


def load_ranfig(file=settings.SETTINGS_DIR):
    config = cp.ConfigParser()
    config.read(file)
    ranfig = {section: {option: config.get(section, option)
                        for option in config.options(section)}
              for section in config.sections()}
    return ranfig

if __name__ == '__main__':
    print load_ranfig()
