from odoo import fields,models,api,_

class StockMoveLine(models.Model):
	_inherit = 'stock.move.line'


	@api.onchange('product_id')
	def _filter_product(self):
		# if self.picking_id.picking_type_id.code == 'outgoing':
		# if self.product_id:
		product_lists = []
		sale_order_line = self.env['sale.order.line'].search([('order_id.name','=', self.picking_id.origin)])
		product_ids = self.env['product.product'].browse(sale_order_line.product_id.ids)
		for rec in product_ids:
			product_lists.append(rec.default_code)

		return {'domain':{'product_id': [('default_code','in',product_lists)]}}