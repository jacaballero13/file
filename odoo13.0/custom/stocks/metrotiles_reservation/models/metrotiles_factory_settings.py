from odoo import models, fields, api, exceptions


class MetrotilesFactorySettings(models.Model):
    _name = 'metrotiles.factory.settings'

    name = fields.Char('Name')

    exchange_rate = fields.Float('Exchange Rate', default=0.0)
    number_factor = fields.Float('Number Factor', default=0.0)

    discount_sqm = fields.Float('Discount (sqm)', default=0.0)
    discount_piece = fields.Float('Discount (piece)', default=0.0)
    discount_mix = fields.Float('Discount (mix)', default=0.0)
    discount_set = fields.Float('Discount (set)', default=0.0)
    discount_others = fields.Float('Discount (others)', default=0.0)

    margin_sqm = fields.Float('Margin% (sqm)', default=0.0)
    margin_piece = fields.Float('Margin% (piece)', default=0.0)
    margin_mix = fields.Float('Margin% (mix)', default=0.0)
    margin_set = fields.Float('Margin% (set)', default=0.0)
    margin_others = fields.Float('Margin% (others)', default=0.0)


class ProductSupplierInfo(models.Model):
    _inherit = 'product.supplierinfo'

    uom = fields.Many2one('uom.uom')