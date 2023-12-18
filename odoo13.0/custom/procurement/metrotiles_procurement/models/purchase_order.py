from datetime import datetime, timedelta
from functools import partial
from itertools import groupby

from odoo import api, fields, models, SUPERUSER_ID, _, exceptions
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import formatLang, get_lang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare

class PurchaseOrder(models.Model):
	_inherit = 'purchase.order'

	status = fields.Selection(selection=[
		('cancelled', "Cancelled"),
		('pending', "Pending"),
		('completed', "Completed")
	], default='pending',required=True, readonly=True, tracking=True)
	proforma_attach = fields.Binary(string="Add Attachment")

class PurchaseOrderLine(models.Model):
	_inherit = 'purchase.order.line'

	remaining_qty = fields.Float(default=0.0)
	variant = fields.Char(string="Variant",
						compute='get_product_details',
						inverse='set_product_details',)
	size = fields.Char(string="Sizes (cm)", 
					compute='get_product_details', 
					inverse='set_product_details',)
    
	series_id = fields.Many2one(comodel_name='metrotiles.series', string='Series', readonly=False, store=True, 
                            compute="get_partner_data")
	partner_id = fields.Many2one(comodel_name="res.partner", 
								readonly=False,
								store=True,
								string="Factory", 
								compute="get_partner_data", 
							)

	@api.depends('product_id')
	def get_product_details(self):
		variant = 'N/A'
		size = 'N/A'
		for rec in self:
			for attr in rec.product_id.product_template_attribute_value_ids:
				if attr.attribute_id.name == 'Variants':
					variant = attr.name
				elif attr.attribute_id.name == 'Sizes':
					size = attr.name
			if rec.product_id.product_template_attribute_value_ids:
				rec.update({'variant': variant, 'size': size})
			else:
				rec.update({'variant': 'N/A', 'size': 'N/A'})

	def set_product_details(self):
		variant = 'N/A'
		size = 'N/A'
		for rec in self:
			for attr in rec.product_id.product_template_attribute_value_ids:
				if attr.attribute_id.name == 'Variants':
					variant = attr.name
				elif attr.attribute_id.name == 'Sizes':
					size = attr.name
			if rec.product_id.product_template_attribute_value_ids:
				rec.update({'variant': variant, 'size': size})
			else:
				rec.update({'variant': 'N/A', 'size': 'N/A'})
	@api.depends('product_id')
	def get_partner_data(self):
		for record in self:
			factory = None
			series = None
			for products in record.product_id:
				if products.variant_seller_ids:
					factory = products.variant_seller_ids[0].name
					# fixed error urgent
				if products:
					series = products.series_id.id
			record.update({
				'partner_id': factory, 'series_id': series,
			})

	@api.model
	def create(self, vals):
		vals['remaining_qty'] = vals['product_qty']
		return super(PurchaseOrderLine, self).create(vals)

	# def write(self, values):
	#     purchase_order_line = super(PurchaseOrderLine, self).write(values)
	#     proforma_items_records = self.env['metrotiles_procurement.proforma_invoice_item'].search(args=[
	#         ('purchase_order_id', '=', self.order_id.id)
	#     ])
	#     total_proforma_items = 0
	#     if len(proforma_items_records):
	#         for proforma_items in proforma_items_records:
	#             if proforma_items.proforma_invoice_id.status == 'approved':
	#                 total_proforma_items += proforma_items.product_qty
	#     item_qty = self.product_qty - total_proforma_items
	#     if item_qty < 0:
	#         raise exceptions.ValidationError("This item has a proforma invoice created!")
	#     purchase_order_line.update({'remaining_qty ':item_qty})
	#     return purchase_order_line

