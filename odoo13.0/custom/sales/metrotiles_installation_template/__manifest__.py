# -*- coding: utf-8 -*-
{
    'name': "metrotiles_installation_template",
    'summary': """
    Installation Printout Template""",
    'description': """
    """,
    'author': "Dats",
    'website': "http://www.metrotilesinc.com",
    'category': 'Report',
    'version': '0.1',
    'depends': ['base','sale','metrotiles_quotation'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/installation_template.xml',
        'views/sale_order.xml'
    ],
}