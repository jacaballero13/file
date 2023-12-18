# -*- coding: utf-8 -*-


{
    'name': 'Inventory Adjustment Enhanced',
    'version': '13.0.0.0',
    'category': 'Inventory',
    'summary': ' ',
    'description': """ """,
    'author': 'Odoo App.',
    'website': 'http://www.Odoo App.com',
    'depends': [
        'base',
        'stock',
        'stock_account',
    ],
    'data': [
        'security/inventory_security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/stock_inventory_views.xml',
        'report/inventory_count_tags_report.xml',
    ],
    'demo': [],
    'images': [],
    'installable': True,
    'auto_install': False,
}

