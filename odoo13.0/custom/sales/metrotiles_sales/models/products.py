from odoo import api, fields, models, SUPERUSER_ID, _

class Product(models.Model):
    _inherit = 'product.template'

    qty_onhand = fields.Float(string='Quantity On Hand',digits=(12,2), default=0, required=True)

    reserved_quantity = fields.Float(digits=(12,2), default=0)


