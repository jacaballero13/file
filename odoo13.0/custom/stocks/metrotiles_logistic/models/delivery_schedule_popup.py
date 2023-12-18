# -*- coding: utf-8 -*-
import logging
from datetime import datetime, timedelta
from functools import partial
from itertools import groupby
from odoo.exceptions import UserError
from odoo import api, fields, models, SUPERUSER_ID, _



class DeliverySchedule(models.TransientModel):
	_name = 'delivery.schedule.popup'


	delivery_contract_id = fields.Many2one("delivery.contract", string="Delivery Contract", required=True,)
	commitment_date = fields.Datetime('Delivery Date')
	allday = fields.Boolean(string='All Day', store=True)
	delivery_area = fields.Many2one('delivery.area', string='Delivery Area')
	track_id = fields.Many2one('fleet.vehicle', string="Track Type")
	trip = fields.Selection([('first_trip', 'First Trip'), ('sec_trip', 'Second Trip')],
							default="first_trip", string="Trip")
	dr_type = fields.Selection([
				('delivery', 'Delivery'),
				('pullout', 'Pullout'),
				('transfer', 'Stock Trasnfer')],
				string='Type of Operation',
				default="delivery",
	)
	def action_confirm(self):
		active_ids = self._context.get('active_ids', [])
		delivery_contract_ids = self.env['delivery.contract'].browse(active_ids)
		contract_ref = delivery_contract_ids.sale_order_id.name
		picking_id = self.env['stock.picking'].search([('picking_type_code', '=', 'outgoing'),('origin','=', contract_ref),('state','!=','cancel')],order='create_date',limit=1)
		
		#Update recorde based on SO reference to Delivery Orders
		delivery_scheudle = self.delivery_contract_id.update({
					'commitment_date': self.commitment_date,
					'track_id': self.track_id.id,
					'delivery_area': self.delivery_area.id,
					'trip': self.trip,
				})
		print(delivery_scheudle)
		#update records and linked to WH related
		if picking_id and picking_id.state in ['assigned','approve']:
			move_to_delivery_outgoing = picking_id.update({
					'delivery_contract_id': delivery_contract_ids.id,
					'scheduled_date': self.commitment_date,
					'track_id': self.track_id.id,
					'delivery_area': self.delivery_area.id,
					'trip': self.trip,
					'x_dr_delivery_date': self.commitment_date
				})
			print(move_to_delivery_outgoing)
		# create records to lineup schedule calendar
		for each in delivery_contract_ids:
			schedule = self.env['calendar.events'].create({
				'delivery_contract_id': delivery_contract_ids.id,
				'delivery_date': self.commitment_date,
				'dr_type': 'delivery',
				'name': each.name,
				'wh_ref': each.wh_ref.id,
				'sale_order_id': each.sale_order_id.id,
				'quotation_type': each.quotation_type,
				'warehouse_id': each.warehouse_id.id,
				'sales_ac': each.sales_ac.id,
				'partner_id': each.partner_id.id,
				'delivery_no': each.delivery_no,
				'delivery_area': each.delivery_area.name,
				'track_id': each.track_id.id,
				'trip': each.trip,
				'responsible_user': each.responsible_user.id,
			})
			print(schedule)
				
