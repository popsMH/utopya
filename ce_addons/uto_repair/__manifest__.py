# -*- coding: utf-8 -*-
{
    'name': "uto_repair",

    'summary': """ Utopya Repair """,

    'description': """
        
    """,

    'author': "Nexources, Henintsoa Moria aka Pops",
    'website': "https://www.nexources.com/",

    # any module necessary for this one to work correctly
    'depends': [
        'uto_base',
        'repair',
        'account',
        'sale',
        'stock'
    ],

    # always loaded
    "data": [
        "security/ir.model.access.csv",
        "data/repair_sequence_data.xml",
        "data/repair_catalog_catalog_data.xml",
        "data/repair_state_data.xml",
        "data/repair_state_helper_data.xml",
        "data/repair_device_data.xml",
        "views/repair_views.xml",
        # "views/accessories_views.xml",
        "views/catalog_catalog_views.xml",
        "views/ecosystem_ecologic_catalog_views.xml",
        "views/utils_views.xml",
        "data/ir_cron.xml",
        "views/account_views.xml",
        "views/report_invoice.xml",
        "views/sale_order_views.xml",
        "views/report_sale_order.xml",
        "report/paper_format.xml",
        "report/report_irreparability_certificate.xml",
        "wizard/api_response_views.xml",
        "wizard/irreparability_certificate_views.xml",
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
