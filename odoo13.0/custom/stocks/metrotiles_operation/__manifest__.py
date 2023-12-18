# -*- coding: utf-8 -*-
{
    'name': "Metrotiles Operation",

    'summary': """
        Operations Details.   
    """,

    'description': """
        Operations Details. and Sale Order Line added Discontinue and Sales items  
    """,

    'author': "Metrotiles Developer",
    'website': "http://metrotiles.com.ph/",
    'category': 'Stock',
    'version': '13.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'metrotiles_partners', 'product', 'sale_management', 'sale', 'metrotiles_reservation', 'metrotiles_quotation'],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/picking_operations.xml',
        'views/detailed.xml',
        'views/product_on_sale.xml',
        'views/picking_wall_location.xml',
        'views/picking_pallet_id.xml',
        'data/sequence.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'auto-install': False, 
}
