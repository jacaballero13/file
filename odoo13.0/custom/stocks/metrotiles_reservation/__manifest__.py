{
    'name': "Metrotiles Reservation",

    'summary': """
        Stock Pre-Reservations""",

    'description': """
        Stock Pre Reservation
    """,

    'author': "Metrotiles Developer",
    'website': "http://metrotiles.com.ph/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales',
    'version': '13.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'metrotiles_quotation', 'sale', 'product', 'stock', 'purchase', 'sale_stock', 'mrp', 'metrotiles_partners', 'metrotiles_intransit'],
    'qweb': ['static/src/xml/fab_sizes.xml', 'static/src/xml/canvas.xml'],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/create_rfq.xml',
        'wizard/product_contract_reserved.xml',
        'wizard/product_temp_reserved.xml',
        'views/inventory_settings.xml',
        'views/sale_order_view.xml',
        'views/metrotiles_fabrication_view.xml',
        'views/product_view.xml',
        'views/purchase_view.xml',
        'views/stock_quant_view.xml',
        'views/res_partner_view.xml'
    ],
    # only loaded in demonstration mode
    'demo': [],
    'installable': True,
    'auto-install': False,
}
