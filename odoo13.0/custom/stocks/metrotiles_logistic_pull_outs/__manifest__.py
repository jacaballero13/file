# -*- coding: utf-8 -*-
{
    'name': "metrotiles_logistics_pull_outs",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",
    'description': """
        Long description of module's purpose
    """,
    'author': "My Company",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'stock', 'metrotiles_sales_adjustment','metrotiles_quotation','sale', 'metrotiles_logistic'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/stock_picking.xml',
        'wizard/pull_out_slip_wizard.xml',
        'views/metrotiles_generated_slips.xml',
        'views/metrotiles_pull_outs.xml',
        'views/metrotiles_pull_outs_menu_items.xml',
        'views/metrotiles_pullouts_schedule_popup.xml',
        'views/calendar_events_inherit.xml',
    ],
}