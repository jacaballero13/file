from odoo import models, fields, api, exceptions


class Designer(models.Model):
    _name = 'metrotiles.designer'

    designer_name = fields.Char('name')
    designer_id = fields.Many2one('res.partner', string="Designer Name", domain=[("category_id.name", "=ilike", "Interior Designer")])
    designer_com_type = fields.Selection(string='Commission type',
                                         selection=[('percentage', 'Percentage'), ('amount', 'Amount')])
    designer_commission = fields.Float(string='Commission')
    designer_sale_id = fields.Many2one(string='sale', comodel_name='sale.order')
    designer_currency_id = fields.Many2one('res.currency', string='Currency')

    designer_initial_price_value = fields.Monetary(related="designer_sale_id.designer_total_price",
                                                   string="Initial Price value",
                                                   currency_field="designer_currency_id", store=True)

    designer_subtotal_price = fields.Monetary(compute='_get_designer_subtotal_price', string="Subtotal", store=True,
                                              currency_field="designer_currency_id")

    @api.depends('designer_com_type', 'designer_commission', 'designer_initial_price_value')
    def _get_designer_subtotal_price(self):
        for price in self:
            if price.designer_com_type == 'percentage':
                price.designer_subtotal_price = ((price.designer_commission or 0.0) / 100) \
                                                * price.designer_initial_price_value
            else:
                price.designer_subtotal_price = price.designer_commission

    # constraint - designer_com_type, designer_commission
    @api.constrains('designer_com_type', 'designer_commission')
    def _validate_designer_commission(self):
        for field in self:
            if field.designer_com_type == 'percentage':
                if (field.designer_commission > 100) or (field.designer_commission <= 0):
                    raise exceptions.ValidationError(
                        "Percentage fields must be less than equal to 100 or greater than 0")

    @api.constrains('designer_id')
    def _validate_designer(self):
        for field in self:
            if field.designer_id.title.name == 'Architect':
                raise exceptions.ValidationError(
                        "Failed")


class DesignerPage(models.Model):
    _inherit = 'sale.order'

    designer_ids = fields.One2many(string="Designer",
                                   comodel_name='metrotiles.designer', inverse_name='designer_sale_id', copy=True)
    designer_total_price = fields.Monetary(store=True, readonly=True, compute='_designer_commission_all',
                                           tracking=4)
    designer_amount_untaxed = fields.Monetary(string="Untaxed Amount", store=True, readonly=True,
                                              compute='_designer_commission_all',
                                              tracking=5)
    designer_amount_tax = fields.Monetary(string="Taxes", store=True, readonly=True, compute='_designer_commission_all')

    designer_total_discount = fields.Float(string="Total Discount", readonly=True, compute='_get_designer_total_price')
    designer_total_discount_rate = fields.Float(string="Total Discount - Percentage", readonly=True,
                                                compute='_get_designer_total_price')
    designer_total_amount = fields.Monetary(string="Total Discount - Amount", readonly=True,
                                            compute='_get_designer_total_price')
    designer_total_commission = fields.Monetary(string="Total Commission", readonly=True,
                                                compute='_get_designer_total_price')
    designer_total_disc_char = fields.Char(compute='_concat_designer_percent', string="Total Discount Rate",
                                           readonly=True)

    @api.depends('designer_total_discount')
    def _concat_designer_percent(self):
        self.designer_total_disc_char = str(self.designer_total_discount) + " %"

    @api.depends('amount_untaxed', 'amount_discount', 'amount_tax')
    def _designer_commission_all(self):
        for rec in self:
            rec.update({
                'designer_total_price': (rec.amount_untaxed - rec.amount_discount),
                'designer_amount_untaxed': rec.amount_untaxed,
                'designer_amount_tax': rec.amount_tax,
            })

    @api.depends('designer_ids', 'designer_total_price')
    def _get_designer_total_price(self):
        for design in self:
            total = 0.0
            total_disc = 0.0
            total_amt = 0.0

            for field in design.designer_ids:
                total += field.designer_subtotal_price
                if field.designer_com_type == 'percentage':
                    total_disc += field.designer_commission
                else:
                    total_amt += field.designer_commission

            design.designer_total_discount_rate = (total_disc / 100) * design.designer_total_price
            design.designer_total_discount = total_disc
            design.designer_total_amount = total_amt
            design.designer_total_commission = total