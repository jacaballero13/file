# -*- coding: utf-8 -*-
{
    'name': "Mix Modules Ehancement",

    'summary': """
        Contains enhancements for the month of June""",
    'description': """
    """,

    'author': "Dats",
    'website': "http://www.metrotilesinc.com",
    'category': 'Enhancements',
    'version': '0.1',
    'depends': ['base','branch','metrotiles_shipments','product','metrotiles_pricing','metrotiles_reservation','metrotiles_commission','account'],
    'data': [
        'views/bol_filter.xml',
        'views/shipment_filter.xml',
        'views/product_view.xml',
        'views/commision_lines.xml',
        'views/account_move.xml',
        'views/sale_order.xml'
        
    ],
}