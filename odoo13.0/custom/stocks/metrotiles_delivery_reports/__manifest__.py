# -*- coding: utf-8 -*-
{
    'name': "Reports for Delivery Receipt, Picking List, Return Slip",

    'summary': """
        Delivery Reports""",

    'description': """
        Detailed Reports for Warehouse Operation
    """,

    'author': "Metrotiles Developer",
    'website': "http://metrotiles.com.ph/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Stock',
    'version': '13.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'sale', 'sale_management', 'branch', 'metrotiles_quotation',],
    # always loaded
    'data': [
        'report/delivery_receipt_footer.xml',
        'report/pull_out_slip.xml',
        'report/action_report_views.xml',
        # 'report/picking_list_footer.xml',
        # 'report/delivery_reciept_documents',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'auto-install': False,
}
