# -*- coding: utf-8 -*-
{
    'name' : "Metrotiles Purchase Advance Payment",
    "author": "Metrotiles Developers",
    'version': '13.0.1.0.0',
    "images":['static/description/main_screenshot.png'],
    'summary': 'Make Advance Payment and Posted Journal Entries from Purchase Order.',
    'description' : """Advance Payment.

     """,
    'depends' : ['purchase','account'],
    'data': [
            'security/advance_payment_group.xml',
            'security/ir.model.access.csv',
            'views/purchase_order_view.xml',
            'wizard/purchase_advance_payment_wizard.xml',
             ],
    'installable': True,
    'auto_install': False,
    'category': 'Accounting',
}
