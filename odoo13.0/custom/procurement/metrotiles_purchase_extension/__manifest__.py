# -*- coding: utf-8 -*-
{
    'name': "Purchase Order Extension",
    'author': 'Metrotiles developers',
    'category': 'Purchase',
    'summary': """Purchase order form""",
    'license': 'AGPL-3',
    'website': 'http://www.metrotiles.com',
    'description': """
""",
    'version': '13.0.1.0.0',
    'depends': ['base','purchase'],
    'data': ['views/purchase_order.xml',
            'report/po_print_template.xml',
            'report/report.xml',
            ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
