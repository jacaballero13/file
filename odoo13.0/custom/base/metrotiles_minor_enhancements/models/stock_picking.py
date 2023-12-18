from odoo import models, fields, api, _
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    delivery_address = fields.Char(related='sale_id.delivery_address')
    invoice_address = fields.Char(related='sale_id.invoice_address')
    ae_name = fields.Char(string='AE', compute='_get_ae_name')

    @api.depends('sale_id','purchase_id')
    def _get_ae_name(self):
        self.ae_name = ''
        for rec in self:
            if rec.sale_id or rec.purchase_id:
                rec.ae_name = rec.sale_id.user_id.name or rec.purchase_id.user_id.name

