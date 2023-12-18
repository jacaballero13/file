# -*- coding: utf-8 -*-
{
    'name': "Metrotiles Logistic",

    'summary': """
        Logistic Operation for Listing contracts to Lineup Shipments and Delivery Schedule""",

    'description': """
        Delivery Schedule based on contracts for Delivery orders and pull out items
    """,

    'author': "Metrotiles Developer",
    'website': "http://www.metrotiles.com.ph",
    'category': 'Sales',
    'version': '13.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'sale_management','fleet', 'stock', 'metrotiles_quotation', 'metrotiles_operation', 'metrotiles_shipments', 'mrp'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/delivery_request_item_view.xml',
        'views/delivery_contract.xml',
        'views/delivery_schedule_popup.xml',
        'views/logistic_schedule.xml',
        'views/sale_order_request.xml',
        'views/delivery_orders_view.xml',
        'views/stock_picking_outgoing_view.xml',
        'views/mrp_production_views.xml',
        'views/sale_order_line.xml',
        'data/sequence.xml',
        

    ],
    # only loaded in demonstration mode
    'demo': [
        #'demo/demo.xml',
    ],
        'installable': True,
        'auto-install': False,
}
