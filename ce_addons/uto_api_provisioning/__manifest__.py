# -*- coding: utf-8 -*-
{
    'name': "uto_api_provisioning",

    'summary': """ Utopya API Provisioning """,

    'description': """
        It is conceived to create company along with users access right
    """,

    'author': "Nexources, Henintsoa Moria aka Pops",
    'website': "https://www.nexources.com/",

    # any module necessary for this one to work correctly
    'depends': [
        'uto_base',
        'web',
        'mail',
        'spreadsheet_dashboard',
        'stock',
        'point_of_sale',
        'gamification',
        'utm',
        'hr',
        'sale',
        'account',
        'sale_management',
        'contacts',
    ],

    # always loaded
    "data": [
        "security/base_groups.xml",
        "security/base_security.xml",
        "security/ir.model.access.csv",
        "views/res_users_views.xml",
        "data/inherit_menus.xml",
        "views/res_partner_views.xml",
        "views/contact_views.xml"
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
