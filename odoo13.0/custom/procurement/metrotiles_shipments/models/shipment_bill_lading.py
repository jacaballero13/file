from datetime import datetime, timedelta
from functools import partial
from itertools import groupby

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import formatLang, get_lang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare


_STATES = [
	('draft', 'Draft'),
	('validate', 'Validated'),
]

class BillOfLading(models.Model): 
	_name = 'shipment.bill_lading'
	_description = "Bill Of Lading"
	_inherit = ['mail.thread']
	_rec_name = 'name'


	name = fields.Char(string="Bill Of Lading", size=32, store=True)

	bill_line = fields.One2many('metrotiles_procurement.proforma_invoice_item', 'shipment_id', 
								string="Bill Lading",  
								readonly=True, store=True)
	shipment_id = fields.Many2one(comodel_name='shipment.number', string="Shipment No.")
	container_no = fields.Many2one(comodel_name="container.number", string="Container No.", readonly=True)
	
	proforma_invoice_id = fields.Many2one(comodel_name="metrotiles_procurement.proforma_invoice", readonly=True)
	partner_id = fields.Many2one(string="Factory", comodel_name='res.partner', related="shipment_id.partner_id", tracking=True)

	xx_ets = fields.Date(string="ETS", required=True, default=datetime.today())
	xx_eta = fields.Date(string="ETA", required=True, default=datetime.today())

	total_inv_qty = fields.Float(string="Total Invoice Qty", compute="get_inv_qty")
	total_ship_qty = fields.Float(string="Total Shipped Qty", compute="get_inv_qty")
	state = fields.Selection(selection=_STATES,
								string='Status',
								index=True,
								track_visibility='onchange',
								required=True,
								copy=False,
								default='draft')
	


	@api.depends('bill_line')
	def get_inv_qty(self):
		amount = 0
		total = 0
		for record in self:
			total =  0
			for po_qty in record.bill_line:
				if po_qty.total_po_qty >= 0:
					amount = po_qty.total_po_qty + po_qty.additional_qty
					total += amount 
				# record.update({
				# 	'total_ship_qty': total,
				# 	'total_inv_qty': total
				# })
			record.total_ship_qty = total
			record.total_inv_qty = total

	def action_validate(self):
		for bol in self:
			has_qty_incoming = 0 
			# proforma_items = self.env['metrotiles_procurement.proforma_invoice_item']
			if not bol.name:
				raise UserError('BOL must be required. Create first ')

			# Use this line of code for intransit qty - but need some logic 
			for bill in self.bill_line:
				has_qty_incoming = bill.total_po_qty
				for each in bill.order_line:
					products = self.env['product.product'].search([('id','=', each.product_id.id)])
					if products and len(bill) > 0:
						intransit_qty = products.incoming_shipments
						products.update({'incoming_shipments': has_qty_incoming + intransit_qty})	
					picking_ids = self.env['stock.picking'].search([('origin', '=', bill.po_reference )])
					if picking_ids:
						picking_ids.update({'shipment_ref': bol.shipment_id.name, 
											'container_ref': bol.container_no.name, 
											'bol_ref': bol.name,
											'xx_ets': bol.xx_ets,
											'xx_eta': bol.xx_eta,
										})
					bol.state = 'validate'
			# proforma = proforma_items.search([('shipment_id', '=', bol.shipment_id.id )])
			# for items in proforma:
			# 	po_reference = items['po_reference']
			# 	purchase_order_id = self.env['purchase.order'].sudo().search([('name', '=', po_reference )])
			# 	if purchase_order_id and purchase_order_id.status == 'completed':
			# 		for purchase in purchase_order_id.order_line:
			# 			product_id = purchase.product_id.id
			# 			has_qty_incoming = purchase['product_qty']
			# 			products = self.env['product.product'].search([('id','=', product_id)], limit=1)
			# 			# for product in products:
			# 			qty_intransit = products.incoming_shipments
			# 			if products.incoming_shipments >= 0:
			# 				products.update({'incoming_shipments':  has_qty_incoming + qty_intransit})
			# 				# bol.status = 'validate'
