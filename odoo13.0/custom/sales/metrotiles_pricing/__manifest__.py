# -*- coding: utf-8 -*-
{
    'name': "Metrotiles Pricing",

    'summary': """
        Pricing.   
    """,

    'description': """
        Pricing.   
    """,

    'author': "Metrotiles Developer",
    'website': "http://metrotiles.com.ph/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales',
    'version': '13.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'product'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv'
        'views/product_template_inherit.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'auto-install': False
}
