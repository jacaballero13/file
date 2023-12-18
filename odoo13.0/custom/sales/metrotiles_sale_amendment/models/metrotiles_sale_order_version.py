from odoo import models, fields, api, exceptions


class SaleOrderVersion(models.Model):
    _name = 'metrotiles.sale.order.version'
    _inherits = {'sale.order': 'sale_order_id'}

    root_sale_order_id = fields.Many2one('sale.order', string="Sale Order")
    version = fields.Integer(string="Version", default=1)

    def get_previous_version(self):
        return self.search(
            [
                ('version', '=', self.version - 1),
                ('root_sale_order_id', '=', self.root_sale_order_id.id)
            ], limit=1)