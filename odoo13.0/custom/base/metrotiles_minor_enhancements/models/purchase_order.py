from odoo import models, fields, api, _
from odoo.exceptions import UserError

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order.line'

    client_name = fields.Char(related='indention_id.customer')
    
    
class ProformaInvoice(models.Model):
    _inherit = 'metrotiles_procurement.proforma_invoice_item'
    
    client_name = fields.Char(compute='_get_po_client_name',store=True)
    so_contract_ref = fields.Many2one(comodel_name='metrotiles.sale.indention',related='order_line.indention_id')
    
    
    @api.depends('order_line')
    def _get_po_client_name(self):
        self.client_name = ''
        
        for rec in self:
            po_obj = self.env['purchase.order.line'].search([('id','=',rec.order_line.id)])
            if po_obj:
                if po_obj.indention_id:
                    rec.client_name = po_obj.indention_id.customer
                    
                else:
                    rec.client_name = ''
