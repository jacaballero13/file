# -*- coding: utf-8 -*-
{
    'name': "so_report_modification",
    'summary': """
        Display only net price of S.O if client need only the net price.""",
    'description': """
    """,
    'author': "METROTILES",
    'website': "http://www.metrotiles.com",
    'category': 'S.O. Report',
    'version': '0.1',
    'depends': ['base','metortiles_totals_and_reports',],
    'data': [
        # 'security/ir.model.access.csv',
        'report/views.xml',
        'report/template.xml',
        'report/so_without_image.xml',
        'report/discount_without_image.xml'
    ],
}