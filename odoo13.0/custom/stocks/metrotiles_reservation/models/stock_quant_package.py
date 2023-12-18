from odoo import models, fields, api, exceptions, _



class StockQuantPackage(models.Model):
    _inherit = 'stock.quant.package'
    _sql_constraints = [ ('pallet_uniq',
                        'UNIQUE (name)',
                        'Pallet already exists'), ]


    
    product_id = fields.Many2one('product.product', string="Product")
    