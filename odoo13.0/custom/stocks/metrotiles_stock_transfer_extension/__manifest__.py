# -*- coding: utf-8 -*-
{
    'name': "Stock Transfer Modification",
    'summary': """
        Inventory modifications module""",
    'description': """
        Contains modifications of inventory
    """,
    'author': "Metrotiles Inc.",
    'website': "http://www.metrotiles.com.ph",
    'category': 'Inventory',
    'version': '0.1',
    'depends': ['base', 'stock','metrotiles_approvals','metrotiles_operation'],
    'data': [
        'views/stock_picking_menu.xml',
        # 'views/inventory_adjustment.xml',
        'views/stock_picking.xml'
    ],
}