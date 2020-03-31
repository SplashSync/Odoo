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
    'version': '0.0.1',
    'category': 'Technical Settings',
    'website': 'https://www.splashsync.com/',
    'author': 'SplashSync',
    'maintainer': 'contact@splashsync.com',
    'license': 'GPL-3',
    'external_dependencies': {
        'python': ["splashpy"],
        'bin': [],
    },
    'depends': [
        'base',
    ],
    'data': [
#        'security/some_model_security.xml',
#        'security/ir.model.access.csv',
#        'views/assets.xml',
       'views/settings_view.xml',
#        'views/res_partner_view.xml',
#        'wizard/wizard_model_view.xml',
    ],
#    'demo': [
#        'demo/res_partner_demo.xml',
#    ],
#    'qweb': [
#        'static/src/xml/module_name.xml',
#    ]
}
