from odoo import api, fields, models
from functools import partial
from itertools import groupby
from odoo.tools.misc import formatLang, get_lang


class ProductTemplate(models.Model):
    _inherit = "product.template"

    taxes_id = fields.Many2many('account.tax', 'product_taxes_rel', 'prod_id', 'tax_id',
                                help="Default taxes used when selling the product.", string='Customer Taxes',
                                domain=[('type_tax_use', '=', 'sale')],
                                default=lambda self: self.default_tax_id())

    def default_tax_id(self):
        params = self.env['ir.config_parameter'].sudo()
        vat_id = int(params.get_param('vat', default=0))
        vat_enabled = bool(params.get_param('vat_enabled', default=False))

        if vat_enabled and vat_id > 0:
            return self.env['account.tax'].sudo().search([('id', '=', vat_id)])
        else:
            return self.env.company.account_sale_tax_id


class SaleOrder(models.Model):
    _inherit = "sale.order"

    vatable = fields.Boolean(string='VAT', default=False)
    amount_tax = fields.Monetary(string='Taxes', store=True, compute='calculate_tax')

    @api.onchange('vatable')
    def onchange_vatable(self):
        for field in self:
            if not field.vatable:
                self.amount_tax = 0.0

            for order_line in field.order_line:
                order_line.tax_id = [(6, 0, [])]

    @api.depends('amount_untaxed', 'amount_discount', 'vatable')
    def calculate_tax(self):
        for rec in self:
            params = self.env['ir.config_parameter'].sudo()
            vat_amount = float(params.get_param('vat_amount', default=0.0))
            amount_tax = 0

            if rec.vatable:
                vat_amount = vat_amount / 100 if vat_amount > 0.0 else 0.0
                discounted_amount = rec.amount_untaxed - rec.amount_discount
                amount_tax = discounted_amount * vat_amount

            rec.update({'amount_tax': amount_tax})

    # MODULE ORIGIN SALE
    @api.depends('order_line.price_total')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal

            order.amount_untaxed = amount_untaxed


    # MODULE ORIGIN METROTILES_DISCOUNT
    @api.depends('total_discounts', 'amount_untaxed')
    def compute_amount_discount(self):
        for order in self:
            amount_untaxed = order.amount_untaxed
            amount_discount = 0.0

            for discount in order.total_discounts:
                if discount.discount_type == 'percentage':
                    percentage = amount_untaxed * (discount.value / 100)

                    amount_discount += percentage
                    amount_untaxed -= percentage
                else:
                    amount_discount += discount.value
                    amount_untaxed -= discount.value

            order.update({'amount_discount': amount_discount})

    def _amount_by_group(self):
        for order in self:
            currency = order.currency_id or order.company_id.currency_id
            fmt = partial(formatLang, self.with_context(lang=order.partner_id.lang).env, currency_obj=currency)
            res = {}
            for line in order.order_line:
                price_reduce = line.price_unit * (1.0 - line.discount / 100.0)
                taxes = line.tax_id.compute_all(price_reduce, quantity=line.product_uom_qty, product=line.product_id,
                                                partner=order.partner_shipping_id)['taxes']
                for tax in line.tax_id:
                    group = tax.tax_group_id
                    res.setdefault(group, {'amount': 0.0, 'base': 0.0})
                    for t in taxes:
                        if t['id'] == tax.id or t['id'] in tax.children_tax_ids.ids:
                            res[group]['amount'] += order.amount_tax
                            res[group]['base'] += t['base']
            res = sorted(res.items(), key=lambda l: l[0].sequence)
            order.amount_by_group = [(
                l[0].name, l[1]['amount'], l[1]['base'],
                fmt(l[1]['amount']), fmt(l[1]['base']),
                len(res),
            ) for l in res]


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _compute_tax_id(self):
        params = self.env['ir.config_parameter'].sudo()
        vat_id = int(params.get_param('vat', default=0))
        vat_enabled = bool(params.get_param('vat_enabled', default=False))
        vat = self.env['account.tax'].sudo().search([('id', '=', vat_id)])

        for line in self:
            if vat_enabled and line.order_id.vatable:
                line.tax_id = vat
            else:
                line.tax_id = []
