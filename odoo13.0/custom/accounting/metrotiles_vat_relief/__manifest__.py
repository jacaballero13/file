# -*- coding: utf-8 -*-
{
    'name': 'Vat Relief',
    'version': '13.0.1.0',
    'depends': [
        'base','account', 'branch'
    ],
    'external_dependencies': {},
    'author': 'Metrotiles',
    'website': 'www.Metrotiles.com',
    'summary': """Vat Releif""",
    'description': """
        Releif
    """,
    'category': 'Accounting',
    'data': [
        'security/ir.model.access.csv',
        'views/metrotiles_bir_slp_views.xml',
        'views/metrotiles_bir_sls_views.xml',
        'views/account_move_inherit_views.xml'
    
    ],
    'installable': True,
    'application': False,
}