# -*- coding: utf-8 -*-
{
    'name': "uto_webclient",

    'summary': """ Utopya Webclient """,

    'description': """
        It is conceived to customize Utopya webclient
    """,

    'author': "Nexources, Henintsoa Moria aka Pops",
    'website': "https://www.nexources.com/",

    # any module necessary for this one to work correctly
    'depends': [
        'uto_base',
        'web',
        'udoo_om_ux'
    ],

    # always loaded
    "data": [
        "views/res_config_settings_views.xml",
        "data/data.xml",
        "wizard/result_test_connection_views.xml",
        "security/ir.model.access.csv",
    ],
    'assets': {
        'web.assets_backend': [
            # 'uto_webclient/static/src/webclient/navbar/*',
            # navbar
            'uto_webclient/static/src/webclient/navbar/navbar.js',
            'uto_webclient/static/src/webclient/navbar/navbar.xml',
            # 'uto_webclient/static/src/webclient/navbar/navbar_extent.xml',
            # widgets
            'uto_webclient/static/src/widgets/res_config_test_connection.js',
            'uto_webclient/static/src/widgets/res_config_test_connection.xml',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
