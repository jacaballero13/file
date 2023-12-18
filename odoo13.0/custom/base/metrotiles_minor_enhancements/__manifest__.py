# -*- coding: utf-8 -*-
{
    'name': "metrotiles_minor_enhancements",
    'summary': """
        Contains minor enhancements starting Feb 2022""",
    'description': """
    """,
    'author': "Dats",
    'website': "http://www.metrotiles.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base','account','purchase','sale','metrotiles_sales_adjustment','app_sale_approval','metrotiles_logistic','metrotiles_procurement'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_move.xml',
        'views/sale_order.xml',
        'views/purchase_order.xml',
        'views/bol.xml',
        'data/sequence.xml',
    ],
}