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

{
    "name": "Splash Sync Connector",
    "version": "20.0.3.0.0",
    "summary": "Synchronize Odoo with any application through Splash Sync",
    "author": "Splash Sync",
    "website": "https://www.splashsync.com",
    "category": "Technical",
    "license": "LGPL-3",
    "depends": ["base", "contacts", "product", "sale_management", "stock", "sale_stock", "account", "website_sale"],
    # splashpy 3.x, betas included (not 4.x)
    "external_dependencies": {"python": ["splashpy>=3.0.0b0,<4"]},
    "data": [
        "views/res_config_settings_views.xml",
    ],
    "images": ["static/description/banner.png"],
    "application": True,
}
