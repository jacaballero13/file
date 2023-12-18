from odoo import models, fields, api, exceptions


class TotalAmountDiscount(models.Model):
    _inherit = 'sale.order'

    column_discounts = fields.Many2many('metrotiles.discount',
                                        'metrotiles_discount_column_sale_order_rel',
                                        string="Column discounts",
                                        domain="([('discount_type','=','percentage')])",
                                        store=False,
                                        default=lambda self: self.get_order_line_discount())

    total_discounts = fields.Many2many('metrotiles.discount',
                                    'metrotiles_discount_total_sale_order_rel',
                                    string="Discounts")

    amount_discount = fields.Float(string='Total Vertical Discount', compute='compute_amount_discount')

    discount_type = fields.Selection(string='Discount Type',
                                     selection=[('percentage', 'Percentage'), ('amount', 'Amount')])

    discount_value = fields.Float(string='Discount Value')

    # amount_discount = fields.Float(string="Discount", compute='compute_discount_recalculate_amount_total')

    # @api.depends('amount_untaxed', 'amount_tax', 'discount_type', 'discount_value')
    # def compute_discount_recalculate_amount_total(self):
    #     """
    #     Compute the total amount of overall discount.
    #     """

    #     for order in self:
    #         total = order.amount_untaxed + order.amount_tax

    #         if order.discount_type == 'percentage':
    #             order.amount_discount = total * (order.discount_value / 100)
    #         else:
    #             order.amount_discount = order.discount_value

    #         order.amount_total = total - order.amount_discount

    def get_order_line_discount(self):
        discounts = []

        for rec in self:
            for line in rec.order_line:
                if line.product_id.product_tmpl_id.type == 'product':
                    discounts = line.discounts
                    break
                else:
                    continue
        return discounts

    @api.onchange('order_line')
    def order_line_changed(self):
        for line in self.order_line:
            if line.product_id.product_tmpl_id.type == 'product':
                line.discounts = self.column_discounts
            else:
                line.discounts = False

    @api.onchange('column_discounts')
    def onchange_column_discounts(self):
        for rec in self:
            if len(rec.column_discounts) > 2:
                raise exceptions.ValidationError("Cannot add more than 2 discounts")

            for line in rec.order_line:
                if line.product_id.product_tmpl_id.type == 'product':
                    line.discounts = self.column_discounts

    @api.onchange('total_discounts')
    def onchange_total_discounts(self):
        for rec in self:
            if len(rec.total_discounts) > 2:
                raise exceptions.ValidationError("Cannot add more than 2 discounts")

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

    @api.depends('discount_type', 'discount_value')
    def format_discount_label(self):
        for field in self:
            if field.discount_type == 'percentage':
                field.update({'label_discount': "Discount {}%".format(field.discount_value)})
            elif field.discount_type == 'amount':
                field.update({'label_discount': "Discount"})
            else:
                field.update({'label_discount': "", 'discount_value': 0})

    @api.constrains('discount_type', 'discount_value')
    def _validate_discount_value(self):
        for field in self:
            if field.discount_type == 'percentage':
                if field.discount_value > 100:
                    raise exceptions.ValidationError(
                        "Percentage fields must be less than or equal to 100")
