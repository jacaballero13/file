from datetime import datetime, timedelta
from functools import partial
from itertools import groupby

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import formatLang, get_lang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare



class ShipmentNumber(models.Model):
	_name = 'shipment.number'
	_inherit = ['mail.thread']
	_rec_name = 'name'


	@api.model
	def _get_default_name(self):
		return self.env['ir.sequence'].get('shipment.number')


	name = fields.Char(string="Shipment Number", size=32, required=True, default=_get_default_name)
	
	proforma_invoice_item = fields.One2many('metrotiles_procurement.proforma_invoice_item', 'shipment_id', required=True, readonly=True)

	weight = fields.Float(string="Total Weight (kg)", compute="compute_weight", default=0, store=True)

	partner_id = fields.Many2one(string="Factory", comodel_name='res.partner', compute="get_partner", tracking=True)

	bill_ids = fields.Many2one(comodel_name='shipment.lading_number', string="Bill lading")

	# added fields for assigning shipments
	
	assign_container_line = fields.One2many('assign_container.popup', 'assign_id', string="Container Details", required=True)

	warehouse_id = fields.Many2one(comodel_name='stock.warehouse', readonly=True, string="Warehouse Location")

	container_no = fields.Many2one(comodel_name="container.number", readonly=True, string="Container Number")

	xx_ets = fields.Date(string="ETS", default=datetime.today())

	xx_eta = fields.Date(string="ETA", default=datetime.today())

	xx_broker = fields.Many2one(comodel_name='assign_container.broker', string="Broker")

	xx_forwarder = fields.Many2one(comodel_name='res.partner', string="Forwarder")

	xx_forwarder_ref = fields.Char('Forwarder Reference No.') 

	xx_consignee = fields.Char(string="Consignee")


	def write(self, values):
		# overriding the write method 
		res = super(ShipmentNumber, self).write(values)
		bill_object = self.env['shipment.bill_lading'].search([])
		for record in self:
			for container in record.assign_container_line:
				if len(container) > 0:
					vals = {}
					vals['container_no'] = container['container_no']
					vals['xx_ets'] = container['xx_ets']
					vals['xx_eta'] = container['xx_eta']
					bill_object.write(vals)
				
		return res



	@api.depends('proforma_invoice_item')
	def get_partner(self):
		for record in self:
			partner_id = ''
			for invoice_lineup in record.proforma_invoice_item:
				partner_id = invoice_lineup.proforma_invoice_id.partner_id.id
				# record.update({
				# 	'partner_id': partner_id,
				# })
			record.partner_id = partner_id

			


	@api.depends('proforma_invoice_item.weight')
	def compute_weight(self):
		for record in self:
			total = 0
			for items in record.proforma_invoice_item:
				total += items.weight
			record.weight = total
