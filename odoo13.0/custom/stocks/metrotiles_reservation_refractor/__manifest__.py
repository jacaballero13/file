# -*- coding: utf-8 -*-
{
    'name': "metrotiles_reservation_refractor",
    'summary': """
        Metrotiles reservation module refractor""",
    'description': """
    """,
    'author': "Dats",
    'website': "",
    'category': 'Enhancements',
    'version': '0.1',
    'depends': ['base', 'sale', 'stock', 'metrotiles_reservation', 'product', 'mrp', 'metrotiles_enhancements', 'sale_stock', 'mti_all_enhancement'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/product_product.xml',
        'views/sale_order_line.xml',
        'data/stock_data.xml'
    ],
}
