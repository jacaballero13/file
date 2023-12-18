# -*- coding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID, _
from datetime import datetime
from odoo.exceptions import UserError


_STATES = [
	('draft', 'Draft'),
	('to_approve', 'Waiting for approval'),
	('approved', 'Approved'),
	('rejected', 'Rejected')
]



class MetrotilesDelivery(models.Model):
	_name = 'delivery.contract'
	_inherit = ['mail.thread']
	_rec_name = 'name'
	_order = 'sale_order_id asc'


	name = fields.Char(string='Reference', copy=False, readonly=True, store=True, compute="get_so_contract")
	delivery_no = fields.Char(string='DR No.',size=32, required=True, default='New')
	wh_ref = fields.Many2one('stock.picking', 'WH Reference')

	sale_order_id = fields.Many2one(comodel_name='sale.order', string="Sales Order", store=True, track_visibility="onchange", )
	quotation_type = fields.Selection([('regular', 'Regular'),('foc', 'Free of Charge'),('installation', 'Installation')],
								default="regular",
								string="Quotation type", related="sale_order_id.quotation_type")

	contract_line = fields.One2many('delivery.contract_line', 'contract_id', string="Contract Order Lines", 
									required=True, store=True)
	warehouse_id = fields.Many2one(comodel_name='stock.warehouse', related="sale_order_id.warehouse_id", string="Warehouse", store=True)
	sales_ac = fields.Many2one(comodel_name= 'res.users', related="sale_order_id.sales_ac", string="Account Coordinator", store=True)
	user_id = fields.Many2one(comodel_name= 'res.users', related="sale_order_id.user_id", string="Salesperson", store=True)

	partner_id = fields.Many2one(comodel_name='res.partner', related="sale_order_id.partner_id", string="Client", store=True)
	dt_created = fields.Datetime('Date', default=datetime.today())

	site_contact = fields.Char(related="sale_order_id.site_contact", string="Site Contact Person")
	site_number = fields.Char(related="sale_order_id.site_number", string="Site Contact Number")
	site_permit = fields.Boolean(string="Requires Permit", related="sale_order_id.site_permit")
	r_permit = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Requires Permit", compute="is_permit")	

	delivery_line_id = fields.Many2one(comodel_name='delivery.line', string="Deliveries Line")
	commitment_date = fields.Datetime(string='Delivery Date')
	delivery_area = fields.Many2one('delivery.area', string='Delivery Area')
	track_id = fields.Many2one('fleet.vehicle', string="Track Type")	
	trip = fields.Selection([('first_trip', 'First Trip'), ('sec_trip', 'Second Trip')],
							default="first_trip", string="Trip",)
	
	delivery_count = fields.Integer(string='Delivery Orders', compute='get_delivery_delivery_count')
	schedule_count = fields.Integer(string='Delivery Schedule', compute='get_delivery_schedule_count')

	is_editable = fields.Boolean(string='Is editable',
								compute="_compute_is_editable",
								readonly=True)
	state = fields.Selection(selection=_STATES,
								string='Status',
								index=True,
								track_visibility='onchange',
								required=True,
								copy=False,
								default='to_approve')
	approve_refused_reason = fields.Char('Refused reason', readonly=True, copy=False, tracking=1)

	responsible_user = fields.Many2one('res.users', 'Responsible', default=lambda self: self.env.user)
	charge_amount = fields.Float('Delivery Charges', compute="_compute_delivery_charge")

	@api.depends('sale_order_id')
	def _compute_delivery_charge(self):
		for rec in self:
			amount = 0.00
			for sale in rec.sale_order_id.charge_ids:
				charge_name = sale.charge_id.name
				if charge_name == 'DELIVERY CHARGE':
					amount += sale.charge_amount

			rec.charge_amount = amount


	@api.depends('r_permit')
	def is_permit(self):
		for record in self:
			if record.site_permit == True:
				record.r_permit = 'yes'
			else:
				record.r_permit = 'no'

	@api.depends('sale_order_id', 'partner_id')
	def get_so_contract(self):
		for contract in self:
			sale_order = contract.sale_order_id.name or ""
			partner = contract.partner_id.name or ""
			contract.name = "DR|[%s] %s" % (sale_order, partner)

	# Smart button that be redirected to delivery orders
	def open_delivery_orders(self):
		return {
			'name': _('Delivery Orders'),
			'domain': [('delivery_contract_id', '=', self.id)],
			'view_type': 'form',
			'res_model': 'stock.picking',
			'view_id': False,
			'view_mode': 'tree,form',
			'type': 'ir.actions.act_window',
		}
	
	# Smart button that be redirected to Logistic Calendar
	def open_delivery_schedule(self):
		return {
			'name': _('Delivery Schedule'),
			'domain': [('delivery_contract_id', '=', self.id)],
			'view_type': 'calendar',
			'res_model': 'calendar.events',
			'view_id': False,
			'view_mode': 'tree,calendar',
			'type': 'ir.actions.act_window',
		}

	def get_delivery_delivery_count(self):
		count = self.env['stock.picking'].search_count([('delivery_contract_id', '=', self.id)])
		self.delivery_count = count

	def get_delivery_schedule_count(self):
		count = self.env['calendar.events'].search_count([('delivery_contract_id', '=', self.id)])
		self.schedule_count = count
	# Add state based on workflow
	@api.depends('state')
	def _compute_is_editable(self):
		for rec in self:
			if rec.state in ('to_approve', 'approved', 'rejected'):
				rec.is_editable = False
			else:
				rec.is_editable = True

	def button_draft(self):
		for rec in self:
			rec.state = 'draft'
		return True

	def button_to_approve(self):
		for rec in self:
			rec.state = 'to_approve'
		return True

	def button_approved(self):
		#update records and linked to WH related
		# once requested delivery approved it will automatically set qty done based on qty requested 
		self.state = 'approved'
		# req_qty_deliver = 0
		for rec in self:
			picking_id = self.env['stock.picking'].search([('picking_type_code', '=', 'outgoing'),('origin','=', rec.sale_order_id.name),('state','!=','cancel')],order='create_date',limit=1)
			self.wh_ref = picking_id.id
		# 	if picking_id and picking_id.state in ['assigned']:
		# 	if picking_id:
		# 		for each in rec.contract_line:
		# 			req_qty_deliver = each.qty_to_deliver
		# 			for pick in picking_id.move_line_ids_without_package:
		# 				if  each.product_id.id == pick.product_id.id:
		# 					pick.update({
		# 						'qty_done': req_qty_deliver,
		# 					})
		# 				rec.wh_ref = picking_id.id
		# 				rec.state = 'approved'
		# 	else:
		# 		raise UserError('Waiting for another operation !')
	def button_rejected(self):
		for rec in self:
			rec.state = 'rejected'
			rec.write({'approve_refused_reason': True })
		return True

	# method to create lineup schedule
	def action_schedule(self):
		view = self.env.ref('metrotiles_logistic.delivery_schedule_popup_form')
		dr_contract = self.env['delivery.schedule.popup'].create({
			'delivery_contract_id': self.id
		})
		return {
			'name': "Create Delivery Schedule",
			'view_mode': 'form',
			'view_id': view.id,
			'res_id': dr_contract.id,
			'view_type': 'form',
			'res_model': 'delivery.schedule.popup',
			'type': 'ir.actions.act_window',
			'target': 'new',
			'context': {
				'default_commitment_date': self.commitment_date,
			}
		}

	def action_generate_dr(self):
		picking_id = self.env['stock.picking'].search([('picking_type_code', '=', 'outgoing'),('origin','=', self.sale_order_id.name)])
		for rec in self:
			if self.delivery_no == 'New' or not None:
				rec['delivery_no'] = self.env['ir.sequence'].next_by_code('delivery.contract') or 'New'
				#once dr generated update delivery no. in WH
				picking_id.update({'delivery_no': rec.delivery_no})
class DeliveryContractLine(models.Model):
	_name = 'delivery.contract_line'
	


	contract_id = fields.Many2one('delivery.contract', string="Delivery Contract")
	
	name = fields.Char(string="Product", store=True)
	display_type = fields.Char('Display Type')

	product_id = fields.Many2one('product.product', string="Description", store=True)

	location_id = fields.Many2one(comodel_name='metrotiles.location', string="Location", store=True)
	application_id = fields.Many2one(comodel_name='metrotiles.application', string="Application", store=True)

	factory_id = fields.Many2one(comodel_name='res.partner', string='Factory',store=True)
	series_id = fields.Many2one(comodel_name='metrotiles.series', string='Series', readonly=False,store=True)

	variant = fields.Char(string="Variant")
	size = fields.Char(string="Sizes (cm)")

	qty_to_deliver = fields.Float(string="Qty to Deliver", default=0, store=True)
	product_uom_qty = fields.Integer(string="Contract Qty",readonly=True, default=None)




