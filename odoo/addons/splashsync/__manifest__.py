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

{
    'name': 'splashsync',
    'summary': 'SplashSync Connector for Odoo',
    'version': "1.15.2",
    'category': 'Technical Settings',
    'website': 'https://www.splashsync.com/',
    'author': 'SplashSync',
    'maintainer': 'contact@splashsync.com',
    'license': 'GPL-3',
    'application': 'true',
    'external_dependencies': {
        'python': ["splashpy"],
        'bin': [],
    },
    'depends': [
        'base', 'product', 'sale',
    ],
    'data': [
       'views/res_config_settings_views.xml',
       'views/product_view.xml',
       'security/ir.model.access.csv',
    ],
    'post_init_hook': 'post_init_hook',
}

