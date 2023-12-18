# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    
    project_name_installation = fields.Char(string="Project")
    re_installation = fields.Char(string="RE:")