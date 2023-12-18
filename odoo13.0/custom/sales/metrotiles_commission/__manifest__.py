# -*- coding: utf-8 -*-
{
    'name': "Metrotiles Commission",

    'summary': """
        Commission Page""",

    'description': """
        Calculates architect and interior designer commission
    """,

    'author': "Metrotiles Developer",
    'website': "http://metrotiles.com.ph/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales',
    'version': '13.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'metrotiles_discount', 'metrotiles_tax'],

    'qweb': [
        "static/src/xml/header_list_view.xml",
        "static/src/xml/header_kanban_view.xml",
    ],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/assets.xml',
        'views/commission_pages.xml',
        'views/res_config_settings.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'auto-install': False,
}
