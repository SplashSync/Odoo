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

import logging
import os


class TestsManager():

    # Test User ID (2 =>> Mitchell Admin)
    __user_id = 2

    @staticmethod
    def init(env):
        """
        Init Odoo & Splashsync Module for Testing
        """
        # ====================================================================#
        # Check if CI Mode is Enabled
        if 'CI_MODE' not in os.environ or os.environ['CI_MODE'] != 'enabled':
            logging.info("[SPLASH][CI] Initialisation Skipped")
            return

        logging.info("[SPLASH][CI] Begin Initialisation")
        # ====================================================================#
        # Setup Test Companies
        companies = {
            "C0": TestsManager.setup_company(env, "YourCompany"),
            "C1": TestsManager.setup_company(env, "PhpUnit1"),
            "C2": TestsManager.setup_company(env, "PhpUnit2")
        }
        logging.info("[SPLASH][CI] Companies Setup Done")
        # ====================================================================#
        # Setup Test User
        TestsManager.setup_users(env)
        logging.info("[SPLASH][CI] User Setup Done")
        # ====================================================================#
        # Setup Splash Configs
        TestsManager.setup_splash(env, companies["C0"], "ThisIsOdooC0WsId", "ThisIsYourEncryptionKeyForSplash")
        TestsManager.setup_splash(env, companies["C1"], "ThisIsOdooC1WsId", "ThisIsYourEncryptionKeyForSplash")
        TestsManager.setup_splash(env, companies["C2"], "ThisIsOdooC2WsId", "ThisIsYourEncryptionKeyForSplash")
        logging.info("[SPLASH][CI] Splash Setup Done")
        # ====================================================================#
        # Ensure Install of an Extra Language
        env['res.lang'].load_lang('fr_FR')
        logging.info("[SPLASH][CI] Languages Setup Done")

    @staticmethod
    def setup_company(env, name: str):
        """
        Setup Odoo Companies for Testing

        :param env:     odoo.Environment
        :param name: str
        :return: void
        """
        # from odoo.addons.splashsync.helpers import CurrencyHelper

        logging.info("[SPLASH][CI] Setup Company "+str(name))

        # ====================================================================#
        # Check if Company Name Exists
        if name == "YourCompany":
            companies = env['res.company'].sudo()._get_main_company()
        else:
            companies = env['res.company'].sudo().search([('name', '=', name)])
        # ====================================================================#
        # Setup a New Company
        if len(companies) == 0:
            logging.info("[SPLASH][CI] Create Company " + str(name))
            company = env['res.company'].sudo().create({
                "name": name,
                "currency_id": 1,
                "phone": "0666066606",
                "email": "odoo@splashsync.com",
                "website": "splashsync.gitlab.io/Odoo",
                "street": "666 avenue des champs Elysees",
                "city": "Paris",
                "country_id": 1,
                "zip": "75033",
            })
        # ====================================================================#
        # Update Company
        else:
            company = companies.ensure_one()
            company.name = name

        logging.info("[SPLASH][CI] Company " + str(name)+" => "+str(company.id))
        return company

    @staticmethod
    def setup_users(env):
        """
        Setup Odoo Users

        :param env:     odoo.Environment
        :return: void
        """
        # ====================================================================#
        # Load Test User
        user = env['res.users'].sudo().browse([TestsManager.__user_id])
        user.ensure_one()
        # ====================================================================#
        # Load list of All Companies
        companies = env['res.company'].sudo().search([])
        # ====================================================================#
        # Ensure Test User is Allowed All Company
        user.company_ids = [(6, 0, companies.ids)]

    @staticmethod
    def setup_splash(env, company, ws_id, ws_key):
        """
        Setup Splashsync Module for a Company

        :param env:     odoo.Environment
        :param company: res.company
        :param ws_id:   str
        :param ws_key:  str
        :return: void
        """
        res_config = env['res.config.splash']
        # ====================================================================#
        # Load Company Config
        config = res_config.get_config(company.id)
        if config is None:
            logging.info("[SPLASH][CI] Create Config for " + str(company.name))
            conf_vals = res_config.get_default_values(company.id)
            conf_vals['ws_user'] = TestsManager.__user_id
            config = res_config.create(conf_vals)
        # ====================================================================#
        # Update Company Parameters
        config.ws_id = ws_id
        config.ws_key = ws_key
        config.ws_expert = True
        config.ws_host = "http://toolkit/ws/soap"
        config.ws_no_commits = False
        # ====================================================================#
        # Detect Default Sales Team
        europe_team = env['crm.team'].name_search("Europe", None, "=", 1)
        sales_team = env['crm.team'].name_search("Sales", None, "=", 1)
        if len(europe_team) > 0:
            config.sales_default_team_id = europe_team[0][0]
        elif len(sales_team) > 0:
            config.sales_default_team_id = sales_team[0][0]
        else:
            raise Exception("[SPLASH] Unable to Detect Default Sale Team")
        # ====================================================================#
        # Save Company Parameters
        config.write(config.get_values())
