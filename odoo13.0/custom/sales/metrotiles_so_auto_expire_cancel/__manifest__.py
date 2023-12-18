# -*- coding: utf-8 -*-
{
    'name': "metrotiles_so_auto_expire_cancel",
    'summary': """
        Auto-cancel S.O contracts if it reach after the expiration date.""",
    'description': """
    """,
    'author': "Dats",
    'website': "http://www.metrotilesinc.ph",
    'category': 'Automation',
    'version': '0.1',
    'depends': ['base','sale'],
    'data': [
        'views/cron.xml'
    ],
}