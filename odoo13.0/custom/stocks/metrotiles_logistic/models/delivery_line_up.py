# -*- coding: utf-8 -*-
from odoo.exceptions import UserError
from odoo.tools.func import default
from odoo.tools.misc import file_open
from odoo import api, fields, models, SUPERUSER_ID, _





_STATES = [
    ('draft', 'NOT YET DELIVERED'),
    ('delivered', 'DELIVERED'),
]

class MetrotilesDelivery(models.Model):
	_name = 'delivery.line'
	_inherit = ['mail.thread']
	_rec_name = 'name'
	

	delivery_item_ids = fields.One2many(string='Deliery Order Lines', comodel_name='delivery.lines.items',  inverse_name='delivery_line_id')
	delivery_contract_id = fields.Many2one(comodel_name='delivery.contract', string="Delivery Contract", required=True)
	name = fields.Char(string='Reference', copy=False, readonly=True, related='delivery_contract_id.name')
	sale_order_id = fields.Many2one(comodel_name='sale.order', related="delivery_contract_id.sale_order_id", string="Sales Order", readonly=True, store=True)
	quotation_type = fields.Selection([('regular', 'Regular'), ('foc', 'Free of Charge'),('installation', 'Installation')],
										default="regular",
										string="Quotation type", related="delivery_contract_id.quotation_type", readonly=True)
	warehouse_id = fields.Many2one('stock.warehouse', related="delivery_contract_id.warehouse_id", readonly=True, string="Warehouse")
	sales_ac = fields.Many2one(comodel_name='res.users', related="delivery_contract_id.sales_ac", readonly=True, string="Account Coordinator")
	partner_id = fields.Many2one(comodel_name='res.partner', related="delivery_contract_id.partner_id", readonly=True, string="Client")

	site_contact = fields.Char(string="Site Contact Person", related="delivery_contract_id.site_contact", readonly=True)
	site_number = fields.Char(string="Site Contact Number", related="delivery_contract_id.site_number", readonly=True)
	site_permit = fields.Boolean(string="Requires Permit", related="delivery_contract_id.site_permit", readonly=True)

	# Field to Create Delivery Schedule popup wizard 
	commitment_date = fields.Datetime('Delivery Date')
	delivery_area = fields.Char('Delivery Area', readonly=True)
	track_id = fields.Many2one('fleet.vehicle', string="Track Type")
	trip = fields.Selection([('first_trip', 'First Trip'), ('sec_trip', 'Second Trip')],
							default="first_trip", string="Trip", readonly=True,)
	
	delivery_no = fields.Char('DR No.', related="delivery_contract_id.delivery_no")
	has_started = fields.Selection(
		string='Has Started',
		default='no',
		selection=[('no', 'No'), ('yes', 'Yes')]
	)
	
	state = fields.Selection(selection=_STATES,
								string='Status',
								index=True,
								track_visibility='onchange',
								required=True,
								copy=False,
								default='draft')
	
	def button_to_delivery(self):
		xx_view = self.env.ref('stock.view_picking_form')
		picking_id = self.env['stock.picking'].search([('picking_type_code', '=', 'outgoing'),('origin','=', self.sale_order_id.name)])
		if picking_id and picking_id.state in ['assigned']:
			sss = picking_id.update({'delivery_no': self.delivery_no})
			print(sss)
		return {
			'name': "Create Delivery",
			'view_mode': 'form',
			'view_id': xx_view.id,
			'res_id': picking_id.id,
			'view_type': 'form',
			'res_model': 'stock.picking',
			'type': 'ir.actions.act_window',
			'target': 'current',
		}



class DeliveryLinesItems(models.Model):
	_name = 'delivery.lines.items'
	_description = "Items Requested to Deliver"


	delivery_line_id = fields.Many2one(comodel_name='delivery.line', string="Delivery Contract")
	
	name = fields.Char(string="Product", store=True)
	display_type = fields.Char('Display Type')

	product_id = fields.Many2one(comodel_name='product.product', string="Description", store=True)

	location_id = fields.Many2one(comodel_name='metrotiles.location', string="Location", store=True)
	application_id = fields.Many2one(comodel_name='metrotiles.application', string="Application", store=True)

	factory_id = fields.Many2one(comodel_name='res.partner', string='Factory',store=True)
	series_id = fields.Many2one(comodel_name='metrotiles.series', string='Series', readonly=False,store=True)

	variant = fields.Char(string="Variant")
	size = fields.Char(string="Sizes (cm)")

	qty_to_deliver = fields.Integer(string="Qty to Deliver", default=0, store=True)
	product_uom_qty = fields.Integer(string="Contract Qty",readonly=True, default=None)

	delivered_qty = fields.Integer(string="Delivered Qty")




