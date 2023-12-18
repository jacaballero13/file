from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order.line'

    unserved_qty = fields.Float(string="Unserved Qty", compute="_compute_unserved_qty")
    
    @api.depends('product_uom_qty', 'qty_delivered')
    def _compute_unserved_qty(self):
        for line in self:
            line.unserved_qty = ( line.product_uom_qty - line.qty_delivered )
