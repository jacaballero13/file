from odoo import models
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def button_mark_done(self):
        res = super(MrpProduction, self).button_mark_done()

        for rec in self:
            sale_id = self.env['sale.order'].search(
                [('name', '=', rec.origin)])

            if sale_id:
                for sales in sale_id.order_line:
                    for lines in rec.finished_move_line_ids:
                        if lines.qty_done == sales.product_uom_qty and lines.product_id.id == sales.product_id.id:
                            self.env['metrotiles.product.reserved'].sudo().create({
                                'stock_location_id': 15,
                                'quantity': lines.qty_done,
                                'sale_line_id': sales.id,
                                'product_id': lines.product_id.id,
                            })

        return res
