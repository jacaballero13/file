# -*- coding: utf-8 -*-
{
    'name': "Metrotiles Cutting Charges",

    'summary': """
        Cutting Charges Computation based on RAW MATERIAL to FINISHED PRODUCT   
    """,

    'description': """
        This will be the additional cutting charge page.
    """,

    'author': "Metrotiles Developer",
    'website': "http://metrotiles.com.ph/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales',
    'version': '13.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'metrotiles_quotation'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_line_views.xml'
        
    ],
    # only loaded in demonstration model
    'installable': True,
    'auto-install': False
}
