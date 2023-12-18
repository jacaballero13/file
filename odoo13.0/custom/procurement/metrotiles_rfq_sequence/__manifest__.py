# -*- coding: utf-8 -*-
{
    'name': "Different Number For PO And RFQ",
    'version': '13.0.1.0.0',
    'category': 'Different Number For PO And RFQ',
    'license': "AGPL-3",
    'summary': " ",
    'author': 'Metrotiles Developers',
    'company': 'Metrotiles Group of Companies',
    'depends': [
                'base','purchase', 'sale'],
    'data': [
            'views/res_config_settings.xml',
            'views/purchase_order.xml'
            ],
    'installable': True,
    'auto_install': False,
    'currency': 'EUR',
}
