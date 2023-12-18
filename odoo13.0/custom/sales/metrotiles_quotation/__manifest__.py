{
    'name': "Metrotiles Quotation",

    'summary': """
        Revise the fields in sales order lines""",

    'description': """
        Fields to be added:
          - application
          - factory
          - series
          - net price
        Revise field:
          - unit_price to gross_price
    """,

    'author': "Metrotiles Developer",
    'website': "http://metrotiles.com.ph/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales',
    'version': '13.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'product', 'sale_management', 'app_sale_approval', 'metrotiles_partners'],
    'qweb': [ 'static/src/xml/locations_subtotal.xml'],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/installation_view.xml',
        'views/account_move_view.xml',
        'views/assets.xml',
        'views/metrotiles_quotation.xml',
        'views/metrotiles_product_item.xml',
        'views/res_config_settings.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'auto-install': False,
}
