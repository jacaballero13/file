from odoo import models, fields, api
from functools import partial
from odoo.tools.misc import formatLang, get_lang


class SaleOrder(models.Model):
    _inherit = "sale.order"
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='calculate_amount_total',
                                   tracking=4)
    materials_net_total = fields.Monetary(string='Materials Net Total', store=True, readonly=True,
                                          compute='calculate_materials_total', tracking=4)
    material_total = fields.Monetary(string='Materials Total', store=True, readonly=True,
                                     compute='calculate_materials_total', tracking=4)

    @api.depends('amount_untaxed', 'amount_discount', 'amount_tax')
    def calculate_materials_total(self):
        for rec in self:
            rec.update({
                'materials_net_total': (rec.amount_untaxed - rec.amount_discount),
                'material_total': (rec.amount_untaxed - rec.amount_discount) + rec.amount_tax
            })

    @api.depends('amount_untaxed', 'amount_discount', 'amount_tax', 'total_charges')
    def calculate_amount_total(self):
        for rec in self:
            rec.update({
                'amount_total': (rec.amount_untaxed - rec.amount_discount) + rec.amount_tax + rec.total_charges
            })
