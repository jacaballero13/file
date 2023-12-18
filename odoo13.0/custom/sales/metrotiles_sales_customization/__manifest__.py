# -*- coding: utf-8 -*-
{
    'name': "metrotiles_sales_customization",
    'summary': """
        Module containing all of sales customization.""",
    'description': """
        Long description of module's purpose
    """,
    'author': "MTI Developer",
    'website': "http://www.metrotilesinc.com",
    'category': 'Sales Customization',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale','account'],
    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/res_partner.xml',
        'views/sale_order.xml'
    ],
}