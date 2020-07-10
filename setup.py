# -*- coding: utf-8 -*-
#
#  This file is part of SplashSync Project.
#
#  Copyright (C) 2015-2020 Splash Sync  <www.splashsync.com>
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  For the full copyright and license information, please view the LICENSE
#  file that was distributed with this source code.
#

from setuptools import setup, find_packages

setup(
       name='splashsync',
       version="0.1.0",
       packages=find_packages(),
       namespace_packages=['odoo.addons.splashsync'],
       install_requires=["splashpy"],
       author='SplashSync',
       author_email='contact@splashsync.com',
       description="Splash Module for Odoo",
       #long_description=open('README.rst').read(),
       license="MIT",
       url='https://github.com/SplashSync/odoo',
       # Active la prise en compte du fichier MANIFEST.in
       #include_package_data=True,
       classifiers=[
              "Programming Language :: Python",
              "Development Status :: 1 - Planning",
              "License :: OSI Approved :: MIT License",
              "Natural Language :: French",
              "Operating System :: OS Independent",
              "Programming Language :: Python :: 3.6",
              "Topic :: Communications",
       ]
)
