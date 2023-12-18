# -*- coding: utf-8 -*-
{
    'name': "Metrotiles Total and Reports",

    'summary': """
        Totals Calculations and reports  
    """,

    'description': """
        Total Calculations and reports  
    """,

    'author': "Metrotiles Developer",
    'website': "http://metrotiles.com.ph/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales',
    'version': '13.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'sale',
        'sale_management',
        'account',
        'metrotiles_quotation',
        'metrotiles_tax',
        'metrotiles_discount',
        'metrotiles_charges'
    ],

    # always loaded
    'data': [
        'views/assets.xml',
        'views/sale_order_view.xml',
        'views/sale_portal_templates.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'auto-install': False
}
