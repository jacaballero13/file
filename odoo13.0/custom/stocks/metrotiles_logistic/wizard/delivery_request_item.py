# -*- coding: utf-8 -*-
import logging
from datetime import datetime, timedelta
from functools import partial
from itertools import groupby
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError

from odoo import api, fields, models, SUPERUSER_ID, _



class DeliveryRequest(models.Model):
	_name = 'delivery.request.item'
	_rec_name = 'sale_order_id'


	order_request_line = fields.One2many('delivery.request.line', 'request_id', string="Order Request Line", store=True)

	sale_order_id = fields.Many2one(comodel_name='sale.order', string="Sales Order", store=True, readonly=True)
	
	quotation_type = fields.Selection([('regular', 'Regular'),('foc', 'Free of Charge'),('installation', 'Installation'), ('sample', 'Sample'), ('foc', 'Free of Charge')], 
										string="Quotation type", readonly=True)
	warehouse_id = fields.Many2one(comodel_name='stock.warehouse', string="warehouse", store=True, readonly=True)
	sales_ac = fields.Many2one(comodel_name='res.users', string="Account Coordinator", readonly=True)
	partner_id = fields.Many2one(comodel_name='res.partner', string="Client", readonly=True)

	site_contact = fields.Char(string="Site Contact Person", readonly=True)
	site_number = fields.Char(string="Site Contact Number", readonly=True)
	site_permit = fields.Boolean(string="Requires Permit", readonly=True)
	


	@api.onchange('sale_order_id')
	def onchange_request_lines(self):
		contract_line = []
		for rec in self:
			if rec.sale_order_id:
				for sale_order in rec.sale_order_id.order_line:
					line = (0,0,{
							'display_type': sale_order.display_type,
							'sequence': sale_order.sequence,
							'name': sale_order.name,
							'product_id': sale_order.product_id.id,
							'location_id': sale_order.location_id.id,
							'application_id': sale_order.application_id.id,
							'factory_id': sale_order.factory_id.id,
							'series_id': sale_order.series_id.id,
							'variant': sale_order.variant,
							'size': sale_order.size,
							'product_uom_qty': sale_order.product_uom_qty,
							'sale_order_line_id': sale_order.id,
							'requested_qty': sale_order.requested_qty,
							'picked_qty' : sale_order.picked_qty
					})
					contract_line.append(line)
				rec.update({'order_request_line': contract_line})
			
			
				
	@api.model		
	def default_get(self, default_fields):
		res = super(DeliveryRequest, self).default_get(default_fields)
		context = self._context
		dr_request = {
			'sale_order_id': context.get('sale_order_id'),
			'quotation_type': context.get('quotation_type'),
			'warehouse_id': context.get('warehouse_id'),
			'partner_id': context.get('partner_id'),
			'sales_ac': context.get('sales_ac'),
			'site_contact': context.get('site_contact'),
			'site_number': context.get('site_number'),
			'site_permit': context.get('site_permit'),
		}
		res.update(dr_request)
		return res

	def create_delivery_req(self):
		has_qty_to_deliver = False
		
		for lines in self.order_request_line:		
			if lines.product_id:
				sale_line = self.env['sale.order.line'].search([('id','=',lines.sale_order_line_id.id)])
				if lines.qty_to_deliver > lines.qty_can_be_requested:
					raise UserError('Cannot request more item than the pick qty - requested qty.')
				sale_line.requested_qty += lines.qty_to_deliver	
			
		for request in self.order_request_line:
			if request.qty_to_deliver > 0:
				has_qty_to_deliver = True
				break

		if has_qty_to_deliver:
			if request.product_uom_qty < request.qty_to_deliver:
				raise UserError("Cannot set request item\'s is greater than contract quantity")
			picking_id = self.env['stock.picking']
			picking_ids = picking_id.search([('origin', '=', self.sale_order_id.name), ('state','in', ['confirmed','assigned','to_approve'])], limit=1)
			warehouse_id = picking_ids.picking_type_id.warehouse_id
			pick = picking_ids.picking_type_id.name
			if warehouse_id and warehouse_id.delivery_steps == 'pick_pack_ship' and pick == 'PICK':
				pass
				#raise ValidationError('Your Item\'s has not been pick {}'.format(self.sale_order_id.name))
			
			delivery_obj = self.env['delivery.contract'].create({'sale_order_id': self.sale_order_id.id})
			pull_out_obj = self.env['metrotiles.pull.outs'].create({'sale_order_id': self.sale_order_id.id,'pullout_type': 'sample',})
			for request in self.order_request_line:
				if self.quotation_type in ('regular','installation', 'foc'):
					self.env['delivery.contract_line'].create({
						'display_type': request.display_type,
						'name': request.name,
						'product_id': request.product_id.id,
						'location_id': request.location_id.id,
						'application_id': request.application_id.id,
						'factory_id': request.factory_id.id,
						'series_id': request.series_id.id,
						'variant': request.variant,
						'size': request.size,
						'product_uom_qty': request.product_uom_qty,
						'qty_to_deliver': request.qty_to_deliver,
						'contract_id': delivery_obj.id,
						})
					
				if self.quotation_type in ('sample'):
					self.env['delivery.contract_line'].create({
						'display_type': request.display_type,
						'name': request.name,
						'product_id': request.product_id.id,
						'location_id': request.location_id.id,
						'application_id': request.application_id.id,
						'factory_id': request.factory_id.id,
						'series_id': request.series_id.id,
						'variant': request.variant,
						'size': request.size,
						'product_uom_qty': request.product_uom_qty,
						'qty_to_deliver': request.qty_to_deliver,
						'contract_id': delivery_obj.id,
						})
					self.env['metrotiles.pull.outs.lines'].create({
						'name': request.name,
						'product_id': request.product_id.id,
						'location_id': request.location_id.id,
						'application_id': request.application_id.id,
						'factory_id': request.factory_id.id,
						'series_id': request.series_id.id,
						'variant': request.variant,
						'size': request.size,
						'product_uom_qty': request.product_uom_qty,
						'pull_out_qty': request.qty_to_deliver,
						'pull_out_id': pull_out_obj.id,
						
				})
		



class DeliveryRequestLine(models.Model):
	_name = 'delivery.request.line'


	request_id = fields.Many2one('delivery.request.item', readonly="True", string="Delivery Request Item")
	
	name = fields.Char(string="Location")
	display_type = fields.Char('Display Type')
	sequence = fields.Char('Sequence')

	product_id = fields.Many2one(comodel_name='product.product', string="Description", store=True)

	location_id = fields.Many2one(comodel_name='metrotiles.location', string="Location", store=True)
	application_id = fields.Many2one(comodel_name='metrotiles.application', string="Application", store=True)

	factory_id = fields.Many2one(comodel_name='res.partner', string='Factory',store=True)
	series_id = fields.Many2one(comodel_name='metrotiles.series', string='Series', readonly=False,store=True)

	variant = fields.Char(string="Variant")
	size = fields.Char(string="Sizes (cm)")

	qty_to_deliver = fields.Integer(string="Qty to Deliver", default=0, store=True)
	product_uom_qty = fields.Integer(string="Contract Qty",readonly=True, default=None)
	sale_order_line_id = fields.Many2one(comodel_name='sale.order.line', store=True)
	requested_qty = fields.Integer(string="Requested Qty",store=True)
	picked_qty = fields.Integer(string="Picked Qty", store=True)
	qty_can_be_requested = fields.Integer(string="Qty can be requested", compute='_compute_picked_request_qty')

	@api.depends('picked_qty','requested_qty')
	def _compute_picked_request_qty(self):
		for rec in self:
			qty = 0
			
			qty = rec.picked_qty - rec.requested_qty
			rec.qty_can_be_requested = qty
 



