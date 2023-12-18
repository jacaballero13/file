# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductProduct(models.Model):
    ######################
    # Private attributes #
    ######################
    _inherit = 'product.product'
    
    
    # type = fields.Selection(selection_add=[('capital', 'Capital Goods')])

