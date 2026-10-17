# -*- coding: utf-8 -*-
{
    'name': "uto_apis",

    'summary': """ Utopya APIs """,

    'description': """
        It is conceived to integrate Ecologic and Ecosystem APIs in Odoo
    """,

    'author': "Nexources, Henintsoa Moria aka Pops",
    'website': "https://www.nexources.com/",

    # any module necessary for this one to work correctly
    'depends': [
        'uto_base',
    ],

    # always loaded
    "data": [
        "security/ir.model.access.csv",
        "views/res_company_views.xml",
        "views/res_config_settings_views.xml",
        "wizard/test_ecosystem_result_wizard_views.xml",
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}