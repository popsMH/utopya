# -*- coding: utf-8 -*-
{
    'name': "uto_stock",

    'summary': """ Utopya Stock""",

    'description': """

    """,

    'author': "Nexources, Henintsoa Moria aka Pops",
    'website': "https://www.nexources.com/",

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'stock',
        'product',
        'sale',
        'point_of_sale',
        'repair',
        'account'
    ],

    # always loaded
    'data': [
        "data/product_data.xml",
        "views/product_views.xml",
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
