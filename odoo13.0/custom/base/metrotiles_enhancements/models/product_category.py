from odoo import models, fields, api

class ProductCategoryInherit(models.Model):
    _inherit = 'product.category'

    product_sub_category = fields.One2many('product.sub.category', 'category_id', string="Sub Category", required=True)