# -*- coding: utf-8 -*-
{
    'name': 'Contract Sales Adjustments',
    'category': 'Sales',
    'version': '13.0.1.0.0',
    'depends': [
        'base',
        'sale', 
        'account',
        'metrotiles_quotation', 
        'metrotiles_cutting_charges', 
        'metrotiles_charges', 
        'metrotiles_discount',
        'metrotiles_commission',
        'app_sale_approval',
        # 'metrotiles_discount',
        # 'metrotiles_logistic_pull_outs'
    ],
    'external_dependencies': {},
    'author': 'Metrotiles',
    'website': 'www.metrotiles.com',
    'summary': """Metrotiles Contract Sales Adjustments""",
    'description': """
        Metrotiles Contract Sales Adjustments 
    """,
    'category': 'Sales',
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/metrotiles_sales_adjustment_data.xml',
        'views/sale_order_adjustment.xml',
        'views/cancel_contract_views.xml',
        'views/cancel_contract_items_views.xml',
        'views/change_designers_views.xml',
        'views/change_charges_views.xml',
        'views/change_item_views.xml',
        'views/change_discount_views.xml',
        'views/change_quantity_views.xml',
        'views/change_vat_views.xml',
        'wizards/metrotiles_saf_wizard.xml',

    ],
    'installable': True,
    'application': False,
}