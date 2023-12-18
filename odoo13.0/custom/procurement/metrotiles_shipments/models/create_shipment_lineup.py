
from datetime import datetime, timedelta
from functools import partial
from itertools import groupby

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import formatLang, get_lang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare



class ProcumentLineupShipment(models.Model):
	_name = 'procurement_shipment.lineup'
	_description = "Proforma Invoice Line Up Shipment"


	shipment_id = fields.Many2one(comodel_name='shipment.number', string="Add Shipment Number", required=True, store=True)


	def action_lineup_shipments(self):
		proforma_lines = self.env['metrotiles_procurement.proforma_invoice_item']
		active_ids = self._context.get("active_ids", [])
		for proforma_invoice in proforma_lines.browse(active_ids):
			proforma_invoice.update({
				'shipment_id': self.shipment_id,
			})
			



