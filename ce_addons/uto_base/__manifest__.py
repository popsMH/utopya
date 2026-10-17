# -*- coding: utf-8 -*-
{
    'name': "uto_base",

    'summary': """ Utopya Base""",

    'description': """

    """,

    'author': "Nexources, Henintsoa Moria aka Pops",
    'website': "https://www.nexources.com/",

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'base_vat',
        'omux_view_action',
        'repair',
        'account',
        'web',
        'portal',
        'account_peppol',
        'sms',
        'mail',
        'udoo_lavend_ux',
        'udoo_om_ux',
        'l10n_fr',
        'base_geolocalize'
    ],

    'assets': {
        'web.assets_backend': [
            (
                'after',
                'omux_view_action/static/src/control_panel.xml',
                'uto_base/static/src/control_panel.xml',
            ),
            (
                'after', 
                'udoo_lavend_ux/static/src/cman/list/controller.xml', 
                'uto_base/static/src/controller.xml'
            ),
            (
                'after', 
                'web/static/src/search/search_bar_menu/search_bar_menu.xml', 
                'uto_base/static/src/search_bar_menu.xml'
            ),
            # ('after', 'udoo_lavend_ux/static/src/cman/list/renderer.xml', 'uto_base/static/src/xml/web_list_renderer.xml'),
        ],
    },

    # always loaded
    'data': [
        "data/occasion_data.xml",
        "views/res_partner_views.xml",
        "views/res_company_views.xml",
        "views/product_template_views.xml",
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
