# -*- coding: utf-8 -*-
{
    'name': "sequence_per_branch",
    'summary': """
        Sequence per branch in invoice and payment""",
    'description': """
        Sequences:
        Invoice
        Customer Payment
        Vendor Bills
        Vendor Payment
    """,
    'author': "Dats",
    'website': "http://www.metrotiles.com",
    'category': 'Sequence',
    'version': '0.1',
    'depends': ['base','account','branch'],
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/views.xml',
        'views/account_move.xml',
        'views/res_branch.xml',
    ],
}