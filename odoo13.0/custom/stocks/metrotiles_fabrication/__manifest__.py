# -*- coding: utf-8 -*-
{
    'name': "Metrotiles Fabrication",

    'summary': """
        Srap process is likely thesame with breakage -This module allows you to recover scrap and will be able to use for fabrication
        if product need to be cut this wil link into manufactoring process + in Receving you can also tag item to fabricate to link on manufactoring 
        for cutting process""",

    'description': """
        - Receiving Items from Picking - Procurment knows what size need to fabricate for cutting based on availability of supplier,
        - Srapping will have an options to choose whether to recover this item into fabrication process or item not be used.
    """,

    'author': "Metrotiles Developers",
    'website': "http://www.metrotiles.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Manufacturing',
    'version': '13.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base','mrp', 'stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/stock_scrap_wizard_popup.xml',
        'views/stock_scrap_extension.xml', 
        'views/stock_picking.xml', 
    ],
    # only loaded in demonstration mode
    'demo': [],
    'installable': True,
    'auto-install': False,
}
