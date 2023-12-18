from odoo import models, fields, api, _
from odoo.exceptions import UserError

class Architecht(models.Model):
    _inherit = 'metrotiles.architect'

    check_payee = fields.Char(string="Check Payee Name")
    
class Designer(models.Model):
    _inherit = 'metrotiles.designer'
    
    check_payee = fields.Char(string="Check Payee Name")