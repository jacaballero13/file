# -*- coding: utf-8 -*-
{
    'name': "Metrotiles Site Contact And Account Coordinator",

    'summary': """
        Site Contact Details and Account Coordinator""",

    'description': """
        Site Contact Details with Document Report Added
        Account Coordinator Field
    """,

    'author': "Metrotiles Developer",
    'website': "http://www.metrotiles.com.ph",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales',
    'version': '13.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'account', 'sale_management'],

    # always loaded
    'data': [
        #'security/ir.model.access.csv',
        'views/site_contact.xml',
        'views/site_contact_templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        #'demo/demo.xml',
    ],
        'installable': True,
        'auto-install': False,
}
