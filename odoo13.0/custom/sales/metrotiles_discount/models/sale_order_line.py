from odoo import models, fields, api, exceptions


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    discounts = fields.Many2many('metrotiles.discount',
                                 string="Horizontal discounts",
                                 relation="metrotiles_discount_order_line_rel",
                                 column1="discount_id",
                                 column2="order_line_id",
                                 domain="([('discount_type','=','percentage',)])")

    @api.depends('product_id', 'price_unit', 'product_uom_qty', 'discounts')
    def _get_net_price(self):
        for line in self:
            total_net = line.price_unit
            for discount in line.discounts:
                if discount.discount_type == 'percentage':
                    total_net = total_net - (total_net * (discount.value / 100))
                else:
                    total_net -= discount.value

            line.update({
                'price_net': total_net,
            })
