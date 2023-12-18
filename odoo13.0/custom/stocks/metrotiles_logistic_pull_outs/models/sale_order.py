from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'
    
    quotation_type = fields.Selection(selection_add=[('sample', 'Sample'),])

    