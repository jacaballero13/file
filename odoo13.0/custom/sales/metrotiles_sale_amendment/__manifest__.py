# -*- coding: utf-8 -*-
{
    'name': "Metrotiles Sale amendment",

    'summary': """
        Sale amendment 
    """,

    'description': """
        Sale amendment
    """,

    'author': "Metrotiles Developer",
    'website': "http://metrotiles.com.ph/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales',
    'version': '13.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'sale_management', 'account', 'metrotiles_discount', 'metrotiles_tax', 'metrotiles_commission', 'metrotiles_quotation'],

    # always loaded
    'data': [
        'data/log_reason_template_data.xml',
        'wizard/metrotiles_amendment_sale_order_reason_wizard.xml',
        'security/ir.model.access.csv',
        'views/assets.xml',
        'views/outdated_sale_order_version.xml',
        'views/pending_sale_adjustment.xml',
        'views/sale_adjustment.xml',
        'views/menu_views.xml',
        'views/sale_order.xml',
    ],
    'qweb': [
        'static/src/xml/sale_amendment_changes.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'auto-install': False
}
