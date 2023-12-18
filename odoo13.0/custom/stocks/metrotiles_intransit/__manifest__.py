# -*- coding: utf-8 -*-
{
    'name': "Metrotiles Incoming Shipments",

    'summary': """
            Adding Incoming Shipments for specific products when bol has been proccessed - also view from sales account coordinator and add date based on delivery date on 
            SO to Manufacturing Deadline 
    """,

    'description': """
        Adding Incoming Shipments to view from sales account coordinator and add date based on delivery date on 
        SO to Manufacturing Deadline   
    """,

    'author': "Metrotiles Developer",
    'website': "http://metrotiles.com.ph/",
    'category': 'Stock',
    'version': '13.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'metrotiles_shipments', 'stock', 'purchase'],
    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/product_product_views.xml',
        

    
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'auto-install': False, 
}
