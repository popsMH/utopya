# -*- coding: utf-8 -*-
{
    'name': "uto_pos",

    'summary': """ Utopya POS """,

    'description': """
        
    """,

    'author': "Nexources, Henintsoa Moria aka Pops",
    'website': "https://www.nexources.com/",

    # any module necessary for this one to work correctly
    'depends': [
        'uto_base',
        'uto_stock',
        'point_of_sale',
        'pos_sale',
    ],

    # always loaded
    "data": [
        'data/pos_category_data.xml',
        'views/pos_config_view.xml',
        'views/report_saledetails_patch.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'uto_pos/static/src/overrides/pos_store_patch.js',
            'uto_pos/static/src/overrides/control_buttons.xml',
            'uto_pos/static/src/overrides/navbar.xml',
            'uto_pos/static/src/overrides/order_summary_patch.js',
            'uto_pos/static/src/overrides/order_summary_patch.xml',
            'uto_pos/static/src/overrides/receipt_screen_patch.xml',
            'uto_pos/static/src/overrides/order_receipt_patch.xml',
            'uto_pos/static/src/overrides/orderline_patch.xml',
            'uto_pos/static/src/overrides/closing_popup_patch.js',
            'uto_pos/static/src/overrides/closing_popup_patch.xml',
            'uto_pos/static/src/overrides/opening_control_popup_patch.js',
            'uto_pos/static/src/overrides/opening_control_popup_patch.xml',
            'uto_pos/static/src/css/uto_pos.css',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
