from odoo import api, fields, models, SUPERUSER_ID, _, exceptions

class Sales(models.Model):
    _inherit = 'sale.order'

    def _action_confirm(self):
        for order in self:
            # if any([expense_policy not in [False, 'no'] for expense_policy in
            #         order.order_line.mapped('product_id.expense_policy')]):
            #     if not order.analytic_account_id:
            #         order._create_analytic_account()

            for order_line in order.order_line:
                order_line.product_id.update({
                    'qty_onhand': order_line.product_id.qty_onhand - order_line.product_uom_qty,
                    'reserved_quantity': order_line.product_id.reserved_quantity + order_line.product_uom_qty
                })

        return True



class SalesOrderLine(models.Model):
    _inherit = 'sale.order.line'


    @api.onchange('product_id', 'product_uom_qty')
    def onchange_sales_order(self):
        for order_line in self:
            if len(order_line.product_id):
                remaining_quantity = order_line.product_id.qty_onhand - order_line.product_id.reserved_quantity
                if order_line.product_uom_qty > remaining_quantity:
                    raise exceptions.ValidationError("To reserve quantity is more than on hand quantity!")

