# -*- coding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID, _



class DeliveryTrack(models.Model):
	_name = 'delivery.track'

	name = fields.Char('Delivery Track')