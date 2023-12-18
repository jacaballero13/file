from odoo import models, fields, api, _
from odoo.exceptions import UserError



class StockPickingInherit(models.Model):
    _inherit = 'stock.picking'
    
#     quotation_type = fields.Selection([
#         ('regular', 'Regular'), 
#         ('installation', 'Installation'),
#         ('sample', 'Sample'),
#         ('foc', 'Free of Charge')],
#         string="Quotation type",compute="get_contract_type", store=True)
