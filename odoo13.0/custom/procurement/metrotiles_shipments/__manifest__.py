# -*- coding: utf-8 -*-
{
    'name': "Metrotiles Shipments",

    'summary': """Manage Shipments""",

    'description': """
        Shipments 
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Procurement',
    'version': '13.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'purchase', 'metrotiles_procurement', 'stock', 'attachment_indexation', 'mail'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/shipment.xml',
        'views/create_shipment_lineup.xml',
        'views/shipment_assign_container.xml',
        'views/shipment_bill_lading.xml',
        'views/proforma_invoice_item.xml',

        #wizard
        'wizards/assign_container_popup.xml',
    

        #user access of the system
        'data/sequence.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
