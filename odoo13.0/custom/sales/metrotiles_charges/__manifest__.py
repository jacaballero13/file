# -*- coding: utf-8 -*-
{
    'name': "Metrotiles Charges",

    'summary': """
        This will implement Metrotiles Charges.     
    """,

    'description': """
        This will implement Metrotiles Charges.   
    """,

    'author': "Metrotiles",
    'website': "http://metrotiles.com.ph",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales',
    'version': '13.0.1.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'metrotiles_discount', 'metrotiles_tax'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/metrotiles_charges.xml',
        'views/metrotiles_name_charges.xml',
        'views/account_move.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'auto-install': False,
}
