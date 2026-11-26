#
#  This file is part of SplashSync Project.
#
#  Copyright (C) Splash Sync  <www.splashsync.com>
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  For the full copyright and license information, please view the LICENSE
#  file that was distributed with this source code.
#

# Test fixtures, run once while building the database image (``odoo shell``, ``env`` is given).
# Companies C0 (main), PhpUnit1, PhpUnit2 with their Splash node, the admin user on all of them.
# Development & tests only: never shipped with the addon.

# ruff: noqa: F821

KEY = "ThisIsYourEncryptionKeyForSplash"
ADMIN_PASSWORD = "admin"  # test stack only: login admin / admin on http://172.120.0.10
TOOLKIT = "http://toolkit.odoo.local/ws/soap"
BASE_URL = "http://app.odoo.local"  # Odoo URL seen by the Toolkit (images, links), frozen
NODES = {"YourCompany": "ThisIsOdooC0WsId", "PhpUnit1": "ThisIsOdooC1WsId", "PhpUnit2": "ThisIsOdooC2WsId"}
VAT = 20.0  # VAT rate of the Toolkit prices
VENDORS = ("Splash Supplies", "BadPixxel Wholesale")  # vendors of the products first supplier
FEATURES = {"Material": ["Cotton", "Wool", "Leather"], "Brand": ["Splash", "BadPixxel"]}

Company = env["res.company"].sudo()

admin = env.ref("base.user_admin")
main = env.ref("base.main_company")
france = env.ref("base.fr")
euro = env.ref("base.EUR")
euro.active = True

companies = []
for name, ws_id in NODES.items():
    company = main if name == "YourCompany" else Company.search([("name", "=", name)], limit=1)
    values = {
        "name": name,
        "street": "666 avenue des Champs Elysees",
        "zip": "75008",
        "city": "Paris",
        "country_id": france.id,
        "phone": "+33 1 23 45 67 89",
        "email": "odoo@splashsync.com",
        "website": "https://www.splashsync.com",
    }
    if not company:
        # created without country: Odoo would install localization modules while running
        company = Company.create({"name": name, "currency_id": euro.id})
    company.write(values)
    company.write(
        {
            "splash_ws_id": ws_id,
            "splash_ws_key": KEY,
            "splash_ws_expert": True,
            "splash_ws_host": TOOLKIT,
            "splash_ws_user_id": admin.id,
        }
    )
    companies.append(company.id)

admin.write({"company_ids": [(6, 0, companies)], "lang": "en_US", "password": ADMIN_PASSWORD})
# English is the default language, French the extra one (translated fields: <field>_fr_FR)
env["res.lang"]._activate_lang("en_US")
env["res.lang"]._activate_lang("fr_FR")
Company.browse(companies).partner_id.write({"lang": "en_US"})
# "Variants" setting enabled: the connector only exposes attributes & variants with it
env["res.config.settings"].create({"group_product_variant": True}).execute()
# Product features: "no variant" attributes; C2 stores them on the variants (Advanced Variants mode)
Attributes = env["product.attribute"]
for name, values in FEATURES.items():
    if not Attributes.search([("name", "=", name), ("create_variant", "=", "no_variant")]):
        Attributes.create(
            {"name": name, "create_variant": "no_variant", "value_ids": [(0, 0, {"name": value}) for value in values]}
        )
Company.search([("name", "=", "PhpUnit2")]).write({"splash_product_advanced_variants": True})
# C1 tests the "Simplified Prices" mode (variants own extra prices)
Company.search([("name", "=", "PhpUnit1")]).write({"splash_product_simplified_prices": True})
# One warehouse per company (companies created after the Inventory module have none)
Warehouses = env["stock.warehouse"].sudo()
for index, company in enumerate(Company.browse(companies)):
    if not Warehouses.search([("company_id", "=", company.id)]):
        Warehouses.create({"name": company.name, "code": f"WH{index}", "company_id": company.id})
# Vendors shared by all companies (products first supplier)
Partners = env["res.partner"].sudo()
for name in VENDORS:
    if not Partners.search([("name", "=", name), ("supplier_rank", ">", 0)]):
        Partners.create({"name": name, "supplier_rank": 1, "company_id": False})
# Toolkit prices are tested with a 20% VAT rate: a sale & a purchase tax of that rate in each company
Taxes = env["account.tax"].sudo()
for company in Company.browse(companies):
    for use in ("sale", "purchase"):
        domain = [("company_id", "=", company.id), ("type_tax_use", "=", use), ("amount_type", "=", "percent")]
        model = Taxes.search(domain, limit=1)
        if model and not Taxes.search([*domain, ("amount", "=", VAT)], limit=1):
            model.copy({"name": f"{VAT:g}% ({use})", "amount": VAT, "price_include_override": "tax_excluded"})
# Base URL: port 80 on the Odoo host, never overwritten by an admin login from another address
Params = env["ir.config_parameter"].sudo()
Params.set_str("web.base.url", BASE_URL)
Params.set_bool("web.base.url.freeze", True)
env.cr.commit()
print(f"[SPLASH] Fixtures done: companies {companies}")
