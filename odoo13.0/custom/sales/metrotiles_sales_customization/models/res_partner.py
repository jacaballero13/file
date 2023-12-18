# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError

class MetrotilesSalesCustom(models.Model):
    _inherit = 'res.partner'
    
    invoice_address = fields.Char(string='Invoice Address')
    delivery_address = fields.Char(string='Delivery Address')
    
  
        
        
    
    # def name_get(self):
    #     result = []
    #     for rec in self:
    #         if rec.child_ids:
    #             result.append((rec.id, "{} {} {}".format(rec.name, rec.type, rec.street)))
    #     return result
            