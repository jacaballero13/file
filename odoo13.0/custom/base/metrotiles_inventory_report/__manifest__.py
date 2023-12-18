# -*- coding: utf-8 -*-
{
    'name': "metrotiles_inventory_report",

    'summary': """
        Metrotiles Excel Inventory Report""",
    'description': """
    """,
    'author': "Dats",
    'website': "http://www.metrotiles.com.ph",
    'category': 'Report',
    'version': '0.1',
    'depends': ['base', 'stock', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'report/inventory_report.xml',
        'wizard/inventory_report_wizard.xml',
    ],
}
