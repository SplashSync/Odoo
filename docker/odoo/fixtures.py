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
ADMIN_PASSWORD = "admin"  # test stack only: login admin / admin on http://localhost:8069
TOOLKIT = "http://toolkit.odoo.local/ws/soap"
NODES = {"YourCompany": "ThisIsOdooC0WsId", "PhpUnit1": "ThisIsOdooC1WsId", "PhpUnit2": "ThisIsOdooC2WsId"}

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
env.cr.commit()
print(f"[SPLASH] Fixtures done: companies {companies}")
