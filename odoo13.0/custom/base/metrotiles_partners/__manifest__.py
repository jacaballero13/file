# -*- coding: utf-8 -*-
{
    'name': "Metrotiles Partners",

    'summary': """Manage User Categories""",

    'description': """
        Metrotiles Partners:
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'base',
    'version': '13.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'product'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',

        #views
        'views/assets.xml',
        'views/res_partner_view.xml',

        #data
        'data/res_partner.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
