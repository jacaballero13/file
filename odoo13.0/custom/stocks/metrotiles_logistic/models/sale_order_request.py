# -*- coding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID, _
from datetime import datetime


class SaleOrder(models.Model):
	_inherit = 'sale.order'


	request_ids = fields.Many2one(
		comodel_name='delivery.request.item',
		string='Delivery Request Line',
	)
	


	def get_delivery_request(self):
		view_id = self.env.ref('metrotiles_logistic.create_delivery_request_form')
		if view_id:
			req_wiz_data = {
				'name': "Delivery Request Line",
				'view_id': view_id.id,
				'view_mode': 'form',
				'view_type': 'form',
				'res_model': 'delivery.request.item',
				'type': 'ir.actions.act_window',
				'target': 'new',
				'context': {
							'sale_order_id': self.id,
							'quotation_type': self.quotation_type,
							'warehouse_id': self.warehouse_id.id,
							'partner_id': self.partner_id.id,
							'sales_ac': self.sales_ac.id,
							'site_contact': self.site_contact,
							'site_number': self.site_number,
							'site_permit': self.site_permit,
							}

			}
		return req_wiz_data


	