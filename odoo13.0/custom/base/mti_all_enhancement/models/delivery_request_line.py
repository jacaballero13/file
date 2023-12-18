from odoo import api, fields, models

class DeliveryRequestLine(models.Model):
	_inherit = 'delivery.request.line'

	balance = fields.Integer(string="Balance to Deliver", compute="_compute_balance_qty", required=True)

	@api.depends('product_uom_qty', 'qty_to_deliver')
	def _compute_balance_qty(self):
		for line in self:
			if line.qty_to_deliver > 0:
				line.balance = (line.product_uom_qty - line.qty_to_deliver)
			else:
				line.balance = 0