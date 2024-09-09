# -*- coding: utf-8 -*-
#
#  This file is part of SplashSync Project.
#
#  Copyright (C) Splash Sync SAS <www.splashsync.com>
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  For the full copyright and license information, please view the LICENSE
#  file that was distributed with this source code.
#

class BomHelper:
    """Collection of Static Functions to manage Product BOMs"""

    @staticmethod
    def get_ascending_ids(product):
        """
        Collect Ids of Ascending Product BOMs
        Product Using this Product in BOM

        :param product: product.product
        :return: dict
        """
        product_ids = list()

        try:
            # ====================================================================#
            # Walk in Product BOM Lines Using this Product
            for bom_line in product.bom_line_ids:
                # ====================================================================#
                # Single Product Selected
                if bom_line.bom_id.product_id.id > 0:
                    product_ids.append(str(bom_line.bom_id.product_id.id))
                    product_ids += BomHelper.get_ascending_ids(bom_line.bom_id.product_id)
                else:
                    # ====================================================================#
                    # Template Product Selected
                    for product_variant_id in bom_line.bom_id.product_tmpl_id.product_variant_ids:
                        product_ids.append(str(product_variant_id.id))
                        product_ids += BomHelper.get_ascending_ids(product_variant_id)
        except Exception:
            pass

        return product_ids

    @staticmethod
    def get_descending_ids(product):
        """
        Collect Ids of Descending Product BOMs
        Product BOM Using this Product

        :param product: product.product
        :return: list
        """

        product_ids = list()

        try:
            # ====================================================================#
            # Walk in Product BOM Using this Product
            for bom in product.bom_ids:
                # ====================================================================#
                # Walk in BOM Lines
                for bom_line in bom.bom_line_ids:
                    # ====================================================================#
                    # Single Product Selected
                    if bom_line.product_id.id > 0:
                        product_ids.append(str(bom_line.product_id.id))
                        product_ids += BomHelper.get_descending_ids(bom_line.product_id)
                    else:
                        # ====================================================================#
                        # Template Product Selected
                        for product_variant_id in bom_line.product_tmpl_id.product_variant_ids:
                            product_ids.append(str(product_variant_id.id))
                            product_ids += BomHelper.get_descending_ids(product_variant_id)
        except Exception:
            pass


        return product_ids
