# -*- coding: utf-8 -*-
{
    'name': "Metrotiles Setup",

    'summary': """
        Install apps.   
    """,

    'description': """
        Metrotiles Installation.   
    """,

    'author': "Metrotiles Developer",
    'website': "http://metrotiles.com.ph/",

    'category': 'Base',
    'version': '13.0.1.0.0',

    'depends': ['base',
                'sale_management',
                'purchase',
                'stock',
                'mrp',
                'l10n_generic_coa',
                # Base
                'metrotiles_partners',
                # Sales
                'metrotiles_quotation',
                'metrotiles_discount',
                'metrotiles_tax',
                'metrotiles_charges',
                'metrotiles_commission',
                'metortiles_totals_and_reports',
                'metrotiles_pricing',
                'metrotiles_site_contact',
                # Procurement
                'metrotiles_distinct_vendor_product'],
    # always loaded
    'data': [
        'data/res_config.xml',
    ],
    'installable': True,
    'auto-install': False
}
