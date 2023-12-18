from odoo import models, fields, api

class ProductProduct(models.Model):
    _inherit = 'product.product'

    pc_box = fields.Integer(string="Piece/Box")
    