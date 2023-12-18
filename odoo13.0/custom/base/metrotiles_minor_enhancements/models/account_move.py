# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    amount_untaxed = fields.Float(digits=(12,2)) 
    
    
    
   