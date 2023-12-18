# from datetime import datetime, timedelta
# from functools import partial
# from itertools import groupby

# from odoo import api, fields, models, SUPERUSER_ID, _
# from odoo.exceptions import AccessError, UserError, ValidationError
# from odoo.tools.misc import formatLang, get_lang
# from odoo.osv import expression
# from odoo.tools import float_is_zero, float_compare




# class ShipmentAssignContainer(models.Model):
# 	_inherit = 'shipment.number'
# 	_description = "Container Details"


# 	def write(self, values):
# 		# overriding the write method 
# 		res = super(ShipmentAssignContainer, self).write(values)
# 		bill_object = self.env['shipment.bill_lading'].search([])
# 		for record in self:
# 			for container in record.assign_container_line:
# 				if len(container) > 0:
# 					vals = {}
# 					vals['container_no'] = container['container_no']
# 					vals['xx_ets'] = container['xx_ets']
# 					vals['xx_eta'] = container['xx_eta']
# 					bill_object.write(vals)
				
# 		return res



# 	assign_container_line = fields.One2many('assign_container.popup', 'assign_id', string="Container Details", required=True)

# 	warehouse_id = fields.Many2one(comodel_name='stock.warehouse', readonly=True, string="Warehouse Location")

# 	container_no = fields.Many2one(comodel_name="container.number", readonly=True, string="Container Number")

# 	xx_ets = fields.Date(string="ETS", default=datetime.today())

# 	xx_eta = fields.Date(string="ETA", default=datetime.today())

# 	xx_broker = fields.Many2one(comodel_name='assign_container.broker', string="Broker")

# 	xx_forwarder = fields.Many2one(comodel_name='res.partner', string="Forwarder")

# 	xx_forwarder_ref = fields.Char('Forwarder Reference No.') 

# 	xx_consignee = fields.Char(string="Consignee")






