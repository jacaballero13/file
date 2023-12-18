# -*- coding: utf-8 -*-
{
    'name': "Metrotiles Credit Memo in Sales Order",

    'summary': """
        Create Credit Memo from Sales Order""",
    'description': """
    """,
    'author': "Metrotiles Developer",
    'website': "http://www.metrotilesinc.com",
    'category': 'sale',
    'version': '0.1',
    'depends': ['base', 'sale', 'account', 'metrotiles_quotation', 'metrotiles_discount','metrotiles_tax'],
    'data': [
        'views/sale_order.xml',
        'wizard/credit_memo_request.xml',
        'views/account_move_inherit.xml',
        'security/ir.model.access.csv',
    ],
}
