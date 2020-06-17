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

from . import OdooObject
from splashpy import const
from .products import ProductsVariants, ProductsAttributes, ProductsPrices, ProductsImages, ProductsFeatures, ProductsRelations


class Product(
    OdooObject,
    ProductsAttributes,
    ProductsVariants,
    ProductsPrices,
    ProductsImages,
    ProductsFeatures,
    ProductsRelations
):
    # ====================================================================#
    # Splash Object Definition
    name = "Product"
    desc = "Odoo Product"
    icon = "fa fa-product-hunt"

    template = None

    @staticmethod
    def getDomain():
        return 'product.product'

    @staticmethod
    def get_listed_fields():
        """Get List of Object Fields to Include in Lists"""
        return ['code', 'name', 'qty_available', 'list_price']

    @staticmethod
    def get_required_fields():
        """Get List of Object Fields to Include in Lists"""
        return ['name']

    @staticmethod
    def get_composite_fields():
        """Get List of Fields NOT To Parse Automaticaly """
        return [
            "id", "valuation", "cost_method", "tracking",
            "image", "image_small", "image_medium", "image_variant",
            "rating_last_image", "rating_last_feedback", "sale_line_warn",
            "message_unread_counter", "purchase_line_warn",
            "price", "lst_price", "list_price", "price_extra", "variant_price_extra", "standard_price",
        ]

    @staticmethod
    def get_configuration():
        """Get Hash of Fields Overrides"""
        return {
            "default_code": {"group": "", "itemtype": "http://schema.org/Product", "itemprop": "model"},
            "name": {"group": "", "itemtype": "http://schema.org/Product", "itemprop": "name"},
            "description": {"group": "", "itemtype": "http://schema.org/Product", "itemprop": "description"},

            "active": {"group": "", "itemtype": "http://schema.org/Product", "itemprop": "active", "notest": True},
            "sale_ok": {"group": "", "itemtype": "http://schema.org/Product", "itemprop": "offered"},
            "purchase_ok": {"group": "", "itemtype": "http://schema.org/Product", "itemprop": "ordered"},

            "qty_available": {"group": ""},
            "qty_at_date": {"group": ""},
            "virtual_available": {"group": ""},
            "outgoing_qty	": {"group": ""},
            "incoming_qty": {"group": ""},

            "website_url": {"type": const.__SPL_T_URL__, "itemtype": "http://schema.org/Product", "itemprop": "urlRewrite"},
            "activity_summary": {"write": False},
            "image": {"group": "", "notest": True},

            "type": {"group": "", "required": False, "itemtype": "http://schema.org/Product", "itemprop": "type"},

            "create_date": {"group": "Meta", "itemtype": "http://schema.org/DataFeedItem", "itemprop": "dateCreated"},
            "write_date": {"group": "Meta", "itemtype": "http://schema.org/DataFeedItem", "itemprop": "dateModified"},
        }

    def order_inputs(self):
        """Ensure Inputs are Correctly Ordered"""
        from collections import OrderedDict
        self._in = OrderedDict(sorted(self._in.items()))

    # ====================================================================#
    # Object CRUD
    # ====================================================================#

    def create(self):
        """Create a New Product with Variants Detection"""
        # ====================================================================#
        # Order Fields Inputs
        self.order_inputs()
        # ====================================================================#
        # Ensure default type
        if "type" not in self._in:
            self._in['type'] = 'product'
        # ====================================================================#
        # Init List of required Fields
        reqFields = self.collectRequiredCoreFields()
        if reqFields is False:
            return False
        # ====================================================================#
        # Create a New Variable Product
        if self.is_new_variable_product():
            # ====================================================================#
            # Detect Product Variant Template
            template_id = self.detect_variant_template()
            if template_id is not None:
                reqFields["product_tmpl_id"] = template_id
        # ====================================================================#
        # Create Product
        new_product = self.getModel().with_context(create_product_product=True).create(reqFields)
        if new_product is None:
            return False
        # ====================================================================#
        # Load Product Template
        for template in new_product.product_tmpl_id:
            self.template = template.with_context(create_product_product=True)
            break

        return new_product

    def load(self, object_id):
        """Load Odoo Object by Id"""
        try:
            # ====================================================================#
            # Order Fields Inputs
            self.order_inputs()
            # ====================================================================#
            # Load Product Variant
            model = self.getModel().browse([int(object_id)])
            if len(model) != 1:
                return False
            # ====================================================================#
            # Load Product Template
            for template in model.product_tmpl_id:
                self.template = template
                break
        except Exception:
            from splashpy import Framework
            Framework.log().warn("Unable to Load Odoo Product " + str(object_id))
            return False

        # self.debug(model, template)

        return model

    def debug( self, product, template):
        """Debug for Product Attributes Configuration"""
        # Debug Product Variants
        infos = "<br />Product Variants: "+str(template.product_variant_ids.ids)
        # Debug Product Attributes
        infos += "<br />Product Values: "
        for prd_value in product.attribute_value_ids:
            infos += "<br /> - "+prd_value.attribute_id.name
            infos += " => "+"["+str(prd_value.id)+"] "+prd_value.name

        # Debug Product Attributes Line
        # infos += "<br />Product Lines: "
        # for prd_line in product.attribute_line_ids:
        #     infos += "<br /> - "+prd_line.attribute_id.name+" Values => "
        #     for value in prd_line.value_ids:
        #         infos += "["+str(value.id)+"] "+value.name
        #     infos += "<br /> - "+prd_line.attribute_id.name+" Template Values => "
        #     for value in prd_line.product_template_value_ids:
        #         infos += "["+str(value.id)+"] "+value.name

        # # Debug Template Attributes Line
        # infos += "<br />Template Lines: "
        # for tmpl_line in template.attribute_line_ids:
        #     infos += "<br /> - "+tmpl_line.attribute_id.name+" Values => "
        #     for value in tmpl_line.value_ids:
        #         infos += "["+str(value.id)+"] "+value.name
        #     infos += "<br /> - "+tmpl_line.attribute_id.name+" Template Values => "
        #     for value in tmpl_line.product_template_value_ids:
        #         infos += "["+str(value.id)+"] "+value.name

        # Debug Product Attributes Line
        infos += "<br />Template Valid Attribute Lines: "
        for prd_line in product.valid_product_template_attribute_line_ids:
            infos += "<br /> - "+prd_line.attribute_id.name+" Values => "
            for value in prd_line.value_ids:
                infos += " ["+str(value.id)+"] "+value.name
            infos += "<br /> - "+prd_line.attribute_id.name+" Template Values => "
            for value in prd_line.product_template_value_ids:
                infos += " ["+str(value.id)+"] "+value.name

        from splashpy import Framework
        Framework.log().dump(infos, "Attributes Debug")
