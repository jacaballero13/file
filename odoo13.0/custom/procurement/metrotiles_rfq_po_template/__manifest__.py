# -*- coding: utf-8 -*-
{
    'name': "RFQ/PO Report Template",
    'summary': """
        Report template for metrotiles RFQ/PO""",
    'description': """
    """,

    'author': "Dats",
    'website': "http://www.metrotilesinc.com",
    'category': 'Reports',
    'version': '0.1',
    'depends': ['base', 'purchase', 'metrotiles_reservation'],
    'data': [
        # 'security/ir.model.access.csv',
        'report/rfq_template.xml',
        'report/po_template.xml',

    ],
}
