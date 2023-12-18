from odoo import models, fields, api, exceptions


class Architect(models.Model):
    _name = 'metrotiles.architect'
    

    architect_name = fields.Char('name')
    architect_id = fields.Many2one('res.partner', string="Architect Name", domain=[("category_id.name", "=ilike", "architect")], track_visibility='onchange')
    architect_com_type = fields.Selection(string='Commission type',
                                          selection=[('percentage', 'Percentage'), ('amount', 'Amount')], track_visibility='onchange')
    architect_commission = fields.Float(string='Commission')
    architect_sale_id = fields.Many2one(string='sale', comodel_name='sale.order', track_visibility='onchange')
    architect_currency_id = fields.Many2one('res.currency', string='Currency', track_visibility='onchange')

    architect_initial_price_value = fields.Monetary(related="architect_sale_id.architect_total_price",
                                                    string="Initial Price value",
                                                    track_visibility='onchange',
                                                    currency_field="architect_currency_id", store=True)

    architect_subtotal_price = fields.Monetary(compute='_get_architect_subtotal_price', string="Subtotal", store=True,
                                               currency_field="architect_currency_id", track_visibility='onchange')

    @api.depends('architect_com_type', 'architect_commission', 'architect_initial_price_value')
    def _get_architect_subtotal_price(self):
        for price in self:
            if price.architect_com_type == 'percentage':
                price.architect_subtotal_price = ((price.architect_commission or 0.0) / 100) \
                                                 * price.architect_initial_price_value
            else:
                price.architect_subtotal_price = price.architect_commission

    # constraint - architect_com_type, architect_commission
    @api.constrains('architect_com_type', 'architect_commission')
    def _validate_architect_commission(self):
        for field in self:
            if field.architect_com_type == 'percentage':
                if (field.architect_commission > 100) or (field.architect_commission <= 0):
                    raise exceptions.ValidationError(
                        "Percentage fields must be less than equal to 100 or greater than 0")


class ArchitectPage(models.Model):
    _inherit = 'sale.order'

    architect_ids = fields.One2many(string="Architect",
                                    comodel_name='metrotiles.architect', inverse_name='architect_sale_id',  copy=True)
    architect_total_price = fields.Monetary(store=True, readonly=True, compute='_architect_commission_all',
                                            tracking=4)
    architect_amount_untaxed = fields.Monetary(string="Untaxed Amount", store=True, readonly=True,
                                               compute='_architect_commission_all',
                                               tracking=5)
    architect_amount_tax = fields.Monetary(string="Taxes", store=True, readonly=True,
                                           compute='_architect_commission_all')

    architect_total_discount = fields.Float(string="Total Discount", readonly=True,
                                            compute='_get_architect_total_price')
    architect_total_discount_rate = fields.Float(string="Total Discount - Percentage", readonly=True,
                                                 compute='_get_architect_total_price')
    architect_total_amount = fields.Monetary(string="Total Discount - Amount", readonly=True,
                                             compute='_get_architect_total_price')
    architect_total_commission = fields.Monetary(string="Total Commission", readonly=True,
                                                 compute='_get_architect_total_price')
    architect_total_discount_char = fields.Char(compute='_concat_architect_percent', string="Total Discount Rate",
                                                readonly=True)

    commission_enabled = fields.Boolean(store=False, default=lambda self: self.get_commission_enabled())

    def get_commission_enabled(self):
        params = self.env['ir.config_parameter'].sudo()

        return bool(params.get_param('commission_enabled', default=False))

    @api.depends('architect_total_discount')
    def _concat_architect_percent(self):
        self.architect_total_discount_char = str(self.architect_total_discount) + " %"

    @api.depends('amount_untaxed', 'amount_discount', 'amount_tax')
    def _architect_commission_all(self):
        for rec in self:
            rec.update({
                'architect_total_price': (rec.amount_untaxed - rec.amount_discount),
                'architect_amount_untaxed': rec.amount_untaxed,
                'architect_amount_tax': rec.amount_tax,
            })

    @api.depends('architect_ids', 'architect_total_price')
    def _get_architect_total_price(self):
        for arch in self:
            total = 0.0
            total_disc = 0.0
            total_amt = 0.0

            for field in arch.architect_ids:
                total += field.architect_subtotal_price
                if field.architect_com_type == 'percentage':
                    total_disc += field.architect_commission
                else:
                    total_amt += field.architect_commission

            arch.architect_total_discount_rate = (total_disc / 100) * arch.architect_total_price
            arch.architect_total_discount = total_disc
            arch.architect_total_amount = total_amt
            arch.architect_total_commission = total
