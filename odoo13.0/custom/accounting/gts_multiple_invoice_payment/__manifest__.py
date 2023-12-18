# -*- coding: utf-8 -*-
{
    'name': 'Multiple Invoice Payment',
    'summary': '''
        Multiple invoices full / partial payment on single payment screen.''',
    'description': '''
        Module allows you to select multiple invoices to pay on payment form. 
        Invoices can be selcted on customer payments and vendor payments. 
        This modules supports partial payment for multiple invoices on single payment screen.
        Multi invoice , easy payment , like version 8 , 9 ''',
    'version': '13.0.11.0.0.3',
    'author': 'Geo Technosoft',
    'website': 'http://www.geotechnosoft.com',
    'company': 'Geo Technosoft',
    "category": "Accounting",
    'depends': ['account','tax_payment_journal'],
    'data': [
        "security/ir.model.access.csv",
        'views/account_payment_view.xml',
        'report/check_voucher_template.xml',
        'report/check_voucher_writer_report.xml',
        'report/check_writer_template.xml'
    ],
    'images': ['static/description/banner.png'],
    'currency':'EUR',
    'license': 'OPL-1',
    'installable': True,
    'application': True,
}
