# -*- coding: utf-8 -*-
{
    'name': "Metrotiles Discount",

    'summary': """
        Additional Discount for every unit price.   
    """,

    'description': """
        This will be the additional discount per unit.
    """,

    'author': "Metrotiles Developer",
    'website': "http://metrotiles.com.ph/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales',
    'version': '13.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'account', 'metrotiles_quotation'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/account_move_view.xml',
        'views/assets.xml',
        'views/discount_view.xml',
        'views/res_config_settings.xml',
        'views/sale_order_discount.xml',
        'views/total_amount_discount.xml',
    ],
    'qweb': [
        'static/src/xml/many2many_discounts.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'auto-install': False
}
