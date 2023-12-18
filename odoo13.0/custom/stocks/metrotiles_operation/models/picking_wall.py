
from odoo import models, fields, api
from odoo.exceptions import UserError


class PickingWall(models.Model):
	_name = 'metrotiles.wall'
	_inherit = ['mail.thread']
	_rec_name = 'wall'

	wall = fields.Char(string="Wall ID", )
	category_id = fields.Many2one('metrotiles.category',string="Wall/Location", required=True, help="Category of wall location")
	


class PickingCategory(models.Model):
	_name = 'metrotiles.category'

	name = fields.Char(string="Wall/Location", help="Category of wall location")
	wall_ids = fields.One2many('metrotiles.wall', 'category_id', readonly=True, string="Wall ID's", help="Can be used for picking stock locations")