from odoo import models, fields, api, exceptions, _



class StockPallet(models.Model):
    _name = 'stock.pallet'
    _rec_name = 'pallet'
    
    name = fields.Char('Pallets')
    location_id = fields.Many2one('stock.location', related='pallet.location_id', string="Location")
    pallet = fields.Many2one('stock.quant.package', string="Pallet")
    product_id = fields.Many2one('product.product', string="Product")
    