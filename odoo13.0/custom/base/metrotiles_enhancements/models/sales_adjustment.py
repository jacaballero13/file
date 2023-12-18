
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SalesAdjustment(models.Model):
    _inherit = 'sales.order.adjustment'

	# sales_ac = fields.Many2one(
	#     comodel_name="res.users", 
	#     related='sale_order_id.user_id',
	#     string="AE"
	# )
	# date_order = fields.Datetime(string='Order Date', related='sale_order_id.date_order')