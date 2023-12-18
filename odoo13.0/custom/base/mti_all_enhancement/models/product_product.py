from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    correct_pricing = fields.Float(string="Public Price1",compute="_get_correct_price",store=True)
    update_pricing = fields.Boolean()
    
    @api.model
    @api.depends('list_price','lst_price','type','pricing_type','update_pricing')
    def _get_correct_price(self):
        pass
        #for rec in self:
          #  rec.correct_pricing = 0
