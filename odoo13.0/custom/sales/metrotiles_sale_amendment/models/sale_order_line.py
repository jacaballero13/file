from odoo import models, fields, api, exceptions

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    previous_version_id = fields.Many2one('metrotiles.sale.order.line.prev.version', string="Previous Version")
    version_status = fields.Char(store=False, string="Version Status")