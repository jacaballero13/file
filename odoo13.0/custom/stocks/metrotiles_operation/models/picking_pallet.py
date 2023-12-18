
from odoo import models, fields, api
from odoo.exceptions import UserError


class PickingWall(models.Model):
	_name = 'metrotiles.pallet'
	_rec_name = 'name'


	@api.model
	def _get_default_name(self):
		return self.env['ir.sequence'].get('metrotiles.pallet')


	name = fields.Char(string="Pallet ID", size=32, default=_get_default_name)
