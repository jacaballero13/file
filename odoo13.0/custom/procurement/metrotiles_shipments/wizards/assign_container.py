from datetime import datetime, timedelta
from functools import partial
from itertools import groupby

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import formatLang, get_lang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare


class ContainerBroker(models.Model):
	_name = 'assign_container.broker'

	name = fields.Char(string="Broker")

class ContainerForwarder(models.Model):
	_name = 'assign_container.forwarder'

	name = fields.Char(string="Forwarder")


class ContainerNumber(models.Model):
	_name = 'container.number'

	name = fields.Char(string="Container Number")


class AssignContainer(models.TransientModel):
	_name = 'assign_container.popup'
	_description = "Terms Popup"
	_rec_name = 'container_no'



	assign_id = fields.Many2one('shipment.assign_container', string="Assigned Container")
	shipment_id = fields.Many2one(comodel_name='shipment.number', string="Shipment No.", readonly=True, default='default_get')
	warehouse_id = fields.Many2one(comodel_name='stock.warehouse', string="Warehouse Location")
	container_no = fields.Many2one(comodel_name='container.number', string="Container No.", required=True)
	xx_ets = fields.Date(string="ETS", required=True, default=datetime.today())
	xx_eta = fields.Date(string="ETA", required=True, default=datetime.today())
	xx_broker = fields.Many2one('assign_container.broker', string="Broker", required=True)
	xx_forwarder = fields.Many2one('res.partner', string="Forwarder", required=True)
	xx_forwarder_ref = fields.Char('Forwarder Reference No.') 
	xx_consignee = fields.Char(string="Consignee")




	def action_assign_container(self):
		shipment_object = self.env['shipment.number'].browse(self._context.get('active_ids', []))
		container_line = shipment_object.assign_container_line
		line = []
		if len(self.container_no) > 0:
			for shipment_reference in shipment_object:
				line.append((0,0,{
					'warehouse_id': self.warehouse_id.id,
					'container_no': self.container_no.id,
					'xx_ets': self.xx_ets,
					'xx_eta': self.xx_eta,
					'xx_broker': self.xx_broker.id,
					'xx_forwarder': self.xx_forwarder.id,
					'xx_forwarder_ref': self.xx_forwarder_ref,
					'xx_consignee': self.xx_consignee,
				}))
				shipment_reference.update({
					'assign_container_line': line,
					'container_no': self.container_no.id
				})

			if len(container_line) >= 1:
				raise ValidationError("You have already Assigned Container")

			# self.env['shipment.bill_lading'].create({
			# 	'shipment_id': self.shipment_id.id,
			# 	'container_no': self.container_no.id,
			# 	'xx_ets': self.xx_ets,
			# 	'xx_eta': self.xx_eta,
			# })

	@api.model
	def default_get(self, default_fields):
		res = super(AssignContainer, self).default_get(default_fields)
		shipment_object = self.env['shipment.number'].browse(self._context.get('active_ids', []))
		res.update({
			'shipment_id': shipment_object.id,
		})
		return res

			

