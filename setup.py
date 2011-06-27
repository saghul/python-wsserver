#!/usr/bin/python
# coding=utf8

# Copyright (C) 2011 Saúl Ibarra Corretgé <saghul@gmail.com>
#

from distutils.core import setup
from wsserver import __version__


setup(name         = "python-wsserver",
      version      = __version__,
      author       = "Saúl Ibarra Corretgé",
      author_email = "saghul@gmail.com",
      url          = "http://github.com/saghul",
      description  = "Basic building blocks for python applications",
      license      = "GPLv3",
      platforms    = ["Platform Independent"],
      py_modules   = ['wsserver'],
      classifiers  = [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL) version 3",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules"
      ])
