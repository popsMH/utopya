# -*- coding: utf-8 -*-
{
    'name': "uto_sales_subscription",

    'summary': """ Utopya Sales Subscription """,

    'description': """

    """,

    'author': "Nexources, Henintsoa Moria aka Pops",
    'website': "https://www.nexources.com/",

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'uto_base',
        'sale_subscription',
    ],

    # always loaded
    "data": [
        "views/product_template_views.xml",
        "views/sale_order_views.xml",
        "views/res_config_settings_views.xml",
        "wizard/result_test_connection_views.xml",
        "security/ir.model.access.csv",
    ],
    'assets': {
        'web.assets_backend': [
            'uto_sale_subscription/static/src/widgets/res_config_test_connection.js',
            'uto_sale_subscription/static/src/widgets/res_config_test_connection.xml',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
