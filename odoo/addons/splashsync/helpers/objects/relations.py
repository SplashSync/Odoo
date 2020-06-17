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

import json
from odoo import http
from splashpy import Framework
from splashpy.helpers.objects import ObjectsHelper


class M2MHelper:
    """Many 2 Many Relations Helper"""

    @staticmethod
    def get_ids(inputs, field):
        """
        Get a Many 2 Many Relation Ids String (JSON)
        :param inputs: str
        :param field: str
        :return: str
        """
        try:
            value_ids = getattr(inputs, field).ids
            if isinstance(value_ids, (dict, list)):
                return json.dumps(value_ids, sort_keys=False)
            return None
        except:
            return None

    @staticmethod
    def set_ids(inputs, field, data, domain=None, filters=[]):
        """
        Set Many 2 Many Relation Records from a Ids String (JSON)
        :param inputs: str      Object to Write
        :param field: str       Field to Write
        :param data: None, str  Json Data to Write
        :param domain: str      Target Objects Domain
        :param filters: list    Additionnal Search Filters
        :return: void
        """
        # ==================================================================== #
        # Validate Input Values
        valid_ids = M2MHelper.__validate_json_ids(data)
        # ==================================================================== #
        # Compare Input Values
        if json.dumps(valid_ids) == M2MHelper.get_ids(inputs, field):
            return
        # ==================================================================== #
        # Verify Values Exists
        verified_ids = M2MHelper.__verify_ids(valid_ids, domain, filters)
        # ==================================================================== #
        # Update M2M ORM Values
        setattr(inputs, field, [(6, 0, verified_ids)])

    @staticmethod
    def set_names(inputs, field, data, index="name", domain=None, filters=[]):
        """
        Set Many 2 Many Relation Records from a Ids String (JSON)
        :param inputs: str      Object to Write
        :param field: str       Field to Write
        :param data: None, str  Json Data to Write
        :param index: str       Property Name
        :param domain: str      Target Objects Domain
        :param filters: list    Additionnal Search Filters
        :return: void
        """
        # ==================================================================== #
        # Validate Input Values
        valid_names = M2MHelper.__validate_json_names(data)
        # ==================================================================== #
        # Verify Values Exists
        verified_ids = M2MHelper.__verify_names(valid_names, index, domain, filters)
        # ==================================================================== #
        # Compare Input Values
        if json.dumps(verified_ids) == M2MHelper.get_ids(inputs, field):
            return
        # ==================================================================== #
        # Update M2M ORM Values
        setattr(inputs, field, [(6, 0, verified_ids)])

    @staticmethod
    def get_names(inputs, field, index="name"):
        """
        Get a Many 2 Many Relation Names String (JSON)
        :param inputs: str
        :param field: str
        :param index: str
        :return: str
        """
        try:
            values = getattr(inputs, field)
            if len(values) == 0:
                return None
            data = []
            for value in values:
                data += [str(getattr(value, index))]
            return json.dumps(data, sort_keys=False)
        except:
            return None

    @staticmethod
    def __validate_json_ids(data):
        """
        Validate Ids String (JSON)
        :param data: None, str  Json Data to Write
        :return: list
        """
        try:
            if data is None or not isinstance(data, str):
                return []
            data_ids = []
            for data_id in json.loads(data):
                data_ids += [int(data_id)]
            return data_ids
        except:
            return []

    @staticmethod
    def __validate_json_names(data):
        """
        Validate Names String (JSON)
        :param data: None, str  Json Data to Write
        :return: list
        """
        try:
            if data is None or not isinstance(data, str):
                return []
            data_ids = []
            for data_id in json.loads(data):
                data_ids += [str(data_id)]
            return data_ids
        except:
            return []

    @staticmethod
    def __verify_ids(data, domain=None, filters=[]):
        """
        Validate Ids
        :param data: list       List of Ids to Write
        :param domain: str      Target Objects Domain
        :param filters: list    Additional Search Filters
        :return: list
        """
        # No Domain or Filter => Skip
        if domain is None or not isinstance(domain, str) or len(domain) < 5:
            return data
        # Execute Domain Search with Filter
        verified_ids = []
        for data_id in data:
            if M2OHelper.verify_id(data_id, domain, filters):
                verified_ids += [int(data_id)]
        return verified_ids

    @staticmethod
    def __verify_names(data, index, domain, filters=[]):
        """
        Validate Ids
        :param data: list       List of Names to Write
        :param index: str       Property Name
        :param domain: str      Target Objects Domain
        :param filters: list    Additional Search Filters
        :return: list
        """
        # Execute Domain Search with Filter
        verified_ids = []
        for data_name in data:
            verified_id = M2OHelper.verify_name(data_name, index, domain, filters)
            if isinstance(verified_id, int):
                verified_ids += [verified_id]
        return verified_ids


class M2OHelper:
    """Many 2 One Relations Helper"""

    @staticmethod
    def get_id(inputs, field):
        """
        Get a Many 2 One Relation Ids String (JSON)
        :param inputs: str
        :param field: str
        :return: str
        """
        try:
            value_id = getattr(inputs, field).id
            if isinstance(value_id, int):
                return value_id
            return None
        except:
            return None

    @staticmethod
    def get_name(inputs, field, index="name"):
        """
        Get a Many 2 One Relation Ids String (JSON)
        :param inputs: str
        :param field: str
        :param index: str
        :return: str
        """
        try:
            return str(getattr(getattr(inputs, field), index))
        except:
            return None

    @staticmethod
    def get_object(inputs, field, object_type):
        """
        Get a Many 2 One Relation Splash Object Ids String
        :param inputs: str
        :param field: str
        :param object_type: str
        :return: str
        """
        object_id = M2OHelper.get_id()
        if isinstance(object_id, int) and object_id > 0:
            return ObjectsHelper.encode(object_type, object_id)
        return None

    @staticmethod
    def get_name_values(domain=None, filters=[]):
        """
        Get a Relation Possible Values Dict
        :param domain: str      Target Objects Domain
        :param filters: list    Additionnal Search Filters
        :return: dict
        """
        # No Domain or Filter => Skip
        if domain is None or not isinstance(domain, str) or len(domain) < 5:
            return True
        # Execute Domain Search with Filter
        results = []
        values = http.request.env[domain].search(filters, limit=50)
        for value in values:
            results += [(value.name, value.name)]
        return results

    @staticmethod
    def set_id(inputs, field, object_id, domain=None, filters=[]):
        """
        Set Many 2 One Relation Records from a Id String/Int
        :param inputs: str      Object to Write
        :param field: str       Field to Write
        :param object_id: None, str, int Data to Write
        :param domain: str      Target Objects Domain
        :param filters: list    Additionnal Search Filters
        :return: void
        """
        # ==================================================================== #
        # Compare Input Values
        if object_id is not None and int(object_id) == M2OHelper.get_id(inputs, field):
            return
        # ==================================================================== #
        # Verify Values Exists
        if M2OHelper.verify_id(object_id, domain, filters):
            # Update M2O ORM Values
            setattr(inputs, field, int(object_id))
        else:
            try:
                setattr(inputs, field, False)
            except:
                pass

    @staticmethod
    def set_name(inputs, field, data, index="name", domain=None, filters=[]):
        """
        Set Many 2 One Relation Records from a Name String
        :param inputs: str      Object to Write
        :param field: str       Field to Write
        :param data: str        Name to Write
        :param index: str       Property Name
        :param domain: str      Target Objects Domain
        :param filters: list    Additionnal Search Filters
        :return: void
        """
        # ==================================================================== #
        # Verify Value
        verified_id = M2OHelper.verify_name(data, index, domain, filters)
        if isinstance(verified_id, int) and verified_id > 0:
            M2OHelper.set_id(inputs, field, verified_id)
        else:
            M2OHelper.set_id(inputs, field, False)

    @staticmethod
    def set_object(inputs, field, field_data, domain=None, filters=[]):
        """
        Set Many 2 One Relation Records from a Splash Object Id String
        :param inputs: str      Object to Write
        :param field: str       Field to Write
        :param field_data:      None, str, int Data to Write
        :param domain: str      Target Objects Domain
        :param filters: list    Additionnal Search Filters
        :return: void
        """
        object_id = ObjectsHelper.id(field_data)
        if isinstance(object_id, int) and object_id > 0:
            return M2OHelper.set_id(inputs, field, object_id, domain, filters)
        return None

    @staticmethod
    def verify_id(object_id, domain=None, filters=[]):
        """
        Validate Id
        :param object_id: None, int, str   Id to Verify
        :param domain: str          Target Objects Domain
        :param filters: list        Additional Search Filters
        :return: bool
        """
        # No Domain or Filter => Skip
        if domain is None or not isinstance(domain, str) or len(domain) < 5:
            return True
        if object_id is None or object_id is False:
            return False
        # Execute Domain Search with Filter
        results = http.request.env[domain].search([('id', '=', int(object_id))] + filters)
        return len(results) > 0

    @staticmethod
    def verify_name(object_name, index, domain, filters=[]):
        """
        Validate Id
        :param object_name: int,str   Id to Verify
        :param index: str       Property Name
        :param domain: str          Target Objects Domain
        :param filters: list        Additional Search Filters
        :return: None, int
        """
        # No Domain or Filter => Skip
        if not isinstance(object_name, str) or not isinstance(index, str) or not isinstance(domain, str):
            return None
        # Execute Domain Search with Filter
        results = http.request.env[domain].search([(index, '=ilike', object_name)] + filters)

        # Results Found => Ok
        if len(results) > 0:
            # More than One Result Found => Ok but Warning
            if len(results) > 1:
                war = "More than One result by name search: "
                war += "'"+object_name+"' Name was found "+str(len(results))+" times"
                war += " on table '"+domain+"'. First value was used."
                Framework.log().warn(war)
            # Return first result
            return results[0].id
        else:
            return None



