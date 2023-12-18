# -*- coding: utf-8 -*-
{
    'name': "Metrotiles Procurement",

    'summary': """Manage trainings""",

    'description': """
        Metrotiles Procurement module for managing trainings:
            - training courses
            - training sessions
            - attendees registration
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Procurement',
    'version': '13.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'purchase', 'mail', 'stock', 'attachment_indexation', 'metrotiles_quotation'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',

        'views/menu.xml',
        'views/proforma_invoice.xml',
        'views/accounting_proforma_invoice.xml',
        'views/cancel_proforma_invoice.xml',
        'views/payment_details_popup.xml',
        'views/terms_popup.xml',
        'views/purchase_order.xml',
        'views/approve_proforma_invoice.xml',
        'views/proforma_terms.xml',
        'views/proforma_items.xml',

        #user access of the system
        # 'data/sequence.xml',
        'data/res.partner.xml',
        'data/menu/res.groups.xml',
        'data/res.users.xml',
        'data/menu/res.procurement_menu.xml',
        'data/menu/res.full_administrator_menu.xml',


        #security access of the system
        'security/administrator.access.xml',
        'security/procurement.access.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
