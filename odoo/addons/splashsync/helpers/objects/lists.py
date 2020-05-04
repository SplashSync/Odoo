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

from abc import abstractmethod
from splashpy.core.framework import Framework


class ListsHelper:

    # ====================================================================#
    # Functions that Parent Class MUST Implements
    # ====================================================================#

    @abstractmethod
    def get_listed_fields(self):
        """Get List of Object Fields to Include in Lists"""
        raise NotImplementedError("Not implemented yet.")

    # ====================================================================#
    # Objects Lists Builder
    # ====================================================================#

    @abstractmethod
    def objectsList(self, filter, params):
        """
        Get Objects List

        :param filter: Search filters to apply (TODO)
        :param params: List pagination
        :return: object
        """
        # ====================================================================#
        # Prepare Search Settings
        try:
            limit = int(params["max"])
        except:
            limit = 25
        try:
            offset = int(params["offset"])
        except:
            offset = 0
        # ====================================================================#
        # Execute Search Query
        results = self.getModel().search([], limit=limit, offset=offset, order='id')
        # Init Results
        objects = {}
        # Walk on Results
        try:
            for result in results.read(self.get_listed_fields()):
                objects["object-" + str(result['id'])] = result
        except Exception as exception:
            Framework.log().fromException(exception)
        # ====================================================================#
        # Add Metadata
        objects['meta'] = {
            'current': results.__len__(),
            'total': self.getModel().search_count([])
        }

        return objects

