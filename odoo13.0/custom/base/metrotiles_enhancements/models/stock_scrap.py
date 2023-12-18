from string import digits
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class StockScrapInherit(models.Model):
    _inherit = 'stock.scrap'

    rso_origin = fields.Char(related='picking_id.origin',)
    product_factory = fields.Many2one(comodel_name='res.partner',
                                      compute='get_product_factory_series')
    product_series = fields.Many2one(comodel_name='metrotiles.series',
                                     compute='get_product_factory_series')
    product_price_unit = fields.Float()
    product_price_subtotal = fields.Float()

    @api.depends('product_id', 'rso_origin')
    def get_product_factory_series(self):
        order_line = []
        for rec in self:
            price_unit = 0
            total = 0
            order_line = self.env['sale.order.line'].search(
                [('order_id.name', '=', rec.rso_origin), ('product_id', '=', rec.product_id.id)])
            for lines in order_line[:1]:
                price_unit = lines.price_net_main_currency
                total = rec.scrap_qty * lines.price_net_main_currency

            rec.product_price_unit = price_unit
            rec.product_price_subtotal = total
            rec.product_factory = rec.product_id.factory_id.id if rec.product_id.factory_id.id else None
            rec.product_series = rec.product_id.series_id.id if rec.product_id.series_id.id else None
