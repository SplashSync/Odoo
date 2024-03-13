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

from splashpy.models import AbstractConfigurator


class ObjectConfigurator(AbstractConfigurator):
    """Odoo Objects Configuration Overrides"""

    config = None

    def __init__(self, object_type, config=None):
        if isinstance(config, dict):
            self.config = {
                object_type: {"fields": config}
            }

    def getConfiguration(self):
        """Return Local Configuration Array"""
        return self.config
