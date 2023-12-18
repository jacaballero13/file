# -*- coding: utf-8 -*-
{
    'name': "metrotiles_manufacturing",
    'summary': """
        Indention module for metrotiles fabrication""",
    'description': """
    """,
    'author': "Metrotiles Developer",
    'website': "http://www.metrotiles.com.ph",
    'category': 'Manufacturing',
    'version': '0.1',
    'depends': ['base','mrp','purchase','metrotiles_fabrication','metrotiles_reservation'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/mrp_production.xml',
        'views/stock_picking.xml',
        'wizard/indent_picking_wizard.xml'
    ],
}
