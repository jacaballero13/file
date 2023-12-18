from custom.sales.metrotiles_quotation.models.metrotiles_series import Series
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    factory = fields.Many2one(comodel_name='res.partner',string='Factory')
    series = fields.Char(string='Series',)
    
    
    
    # @api.depends('product_id')
    # def get_pallet_id(self):
    #     prod_obj = self.env['product.product'].search([('id', '=', self.product_id.id)])
            
    #     for rec in self:
    #         if prod_obj:
    #             self.factory = prod_obj.seller_ids[0].name if prod_obj.seller_ids else False
    #             self.series = prod_obj.series_id.description_name
    #             break
                
    