from odoo import models, fields, api, _
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit = 'stock.move.line'
    
    factory_id = fields.Many2one(comodel_name='metrotiles.factory.settings')

    