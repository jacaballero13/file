from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SalesOrder(models.Model):
    _inherit = 'sale.order'
    
    is_delivery_request = fields.Boolean(default=False)
    
    def action_check(self):
        res = super(SalesOrder, self).action_check()
        self.write({'is_delivery_request': True})
        return res
    
    @api.model
    def create(self, vals):
        quot_type = vals.get('quotation_type')

        if quot_type == 'foc':
            vals['name'] = self.env['ir.sequence'].next_by_code('s.o.foc.sequence')
            
        return super(SalesOrder, self).create(vals)
class SalesOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # rif = fields.Char(string="RIF", default='0|0|0', compute="get_rif", store=True)
    