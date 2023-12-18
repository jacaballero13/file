{
    'name': 'Withholding Tax on Payments',
    'version': '13.0.1.0.0',
    'category': 'accouting',
    'license': "AGPL-3",
    'summary': " ",
    'author': 'Itech resources',
    'company': 'ItechResources',
    'depends': [
                'sale',
                'purchase',
                'account',
                ],
    'data': [

            'views/account_tax.xml',
            'views/payment_view.xml',
            # 'views/multi_payments_view.xml'
            
            ],
    'installable': True,
    'auto_install': False,
    'price':'80.0',
    'currency': 'EUR',
}
