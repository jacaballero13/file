# -*- coding: utf-8 -*-
{
    'name': "Metrotiles Distinct Vendor Product",

    'summary': """
        This will separate products according to supplier.   
    """,

    'description': """
        This will separate products according to supplier.
    """,

    'author': "Metrotiles Developer",
    'website': "http://metrotiles.com.ph/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Purchase',
    'version': '13.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'purchase', 'product'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/metrotiles_distinct_product.xml',
        'views/supplier_info_view.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'auto-install': False,
}
