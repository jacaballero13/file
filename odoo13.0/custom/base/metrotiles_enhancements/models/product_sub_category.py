from odoo import models, fields, api

class ProductSubCategory(models.Model):
    _name = 'product.sub.category'
    _rec_name = 'name'

    name = fields.Char("Name")
    category_id = fields.Many2one('product.category', string="Category")