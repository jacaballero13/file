from odoo import models, fields, api, exceptions


class SaleOrderLineChanges(models.Model):
    _inherit = "sale.order"

    order_line_changes = fields.One2many('sale.order.line', store=False, compute="get_order_line_changes")

    def get_order_line_changes(self):
        for rec in self:
            prev = rec.sale_order_version_id.get_previous_version()
            order_lines = rec.env['sale.order.line'].search(
                ['|', ('order_id', '=', prev.sale_order_id.id), '&', ('display_type','=', None), '&', ('previous_version_id', '=', None), ('order_id', '=', rec.id)], order="id asc")

            rec.update({'order_line_changes': order_lines})

            return order_lines

