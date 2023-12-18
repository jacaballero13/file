# -*- coding: utf-8 -*-
{
    'name': "metrotiles_enhancements",
    'summary': """
        Containts all of metrotiles enhancements starting December.""",
    'description': """
        - S.O Sequence
        - Stock Quant product columns
        - Branch
    """,
    'author': "METROTILES",
    'website': "http://www.metrotiles.com.ph",
    'category': 'Enhancements',
    'version': '0.1',
    'depends': ['base',
        'app_sale_approval', 
        'metrotiles_discount', 
        'metrotiles_procurement', 
        'metrotiles_operation', 
        'metrotiles_reservation',
        'account', 
        'sale', 
        'branch', 
        'purchase', 
        'stock', 
        'product', 
        'metrotiles_sales_adjustment',
        'metrotiles_quotation', 
        'metrotiles_tax',
        'mti_all_enhancement',
        'metrotiles_commission'],
    'data': [
        'security/ir.model.access.csv',
        'security/sale_security.xml',
        'views/res_branch.xml',
        'data/sequence.xml',
        'views/purchase_order.xml',
        'views/stock_quant.xml',
        'views/sale_order.xml',
        'views/account_payment.xml',
        'views/account_move.xml',
        'views/stock_move.xml',
        'views/proforma_invoice_item.xml',
        'views/stock_scrap.xml',
        'views/product_product.xml',
        'views/stock_warehouse.xml',
        'views/res_partner.xml',
        'views/designer.xml',
        'views/architect.xml',
        'views/product_sub_category.xml',
        'views/mrp_production.xml',
        'report/purchase_order_footer.xml'
    ],
}
