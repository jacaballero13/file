from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ResBranch(models.Model):
    _inherit = 'res.branch'
    
    branch_sequence = fields.Char(string='Sequence Prefix')

    