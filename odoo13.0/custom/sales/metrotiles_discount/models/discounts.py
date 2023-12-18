from odoo import models, fields, api, exceptions


class Discounts(models.Model):
    _name = "metrotiles.discount"
    _descriptions = "To Enable Multiple Discounts"

    name = fields.Char(string='name')

    discount_type = fields.Selection([('percentage', 'Percentage'), ('amount', 'Amount')],
                                     string="Discount Type",
                                     default=lambda self: self.default_type())

    is_discount_type_editable = fields.Boolean(compute='default_type', default=lambda self: self.default_is_discount_type_editable())

    value = fields.Float(string='Value', default=0.0)

    def default_type(self):
        return self.env.context.get('discount_type')

    def default_is_discount_type_editable(self):
        return self.env.context.get('discount_type_editable', True)

    @api.constrains('discount_type', 'value')
    def _validate_architect_commission(self):
        for field in self:
            if field.discount_type == 'percentage':
                if (field.value > 100) or (field.value <= 0):
                    raise exceptions.ValidationError(
                        "Percentage fields must be less than equal to 100 or greater than 0")
            if not field.discount_type:
                    raise exceptions.ValidationError(
                        "Discount type is required field")

    @api.model
    def create(self, vals):
        percent_sign = '%' if vals['discount_type'] == 'percentage' else ''
        vals['name'] = "{}{}".format(vals['value'], percent_sign)

        return super(Discounts, self).create(vals)
