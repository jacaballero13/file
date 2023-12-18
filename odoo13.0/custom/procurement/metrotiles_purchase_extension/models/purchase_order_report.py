# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def run_sql(self, qry):
        self._cr.execute(qry)
        _res = self._cr.dictfetchall()
        return _res
    
    def print_po(self):
        return self.env.ref('metrotiles_purchase_extension.purchase_form_print').report_action(self)
    
class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    
    prod_desc = fields.Char(string='Description')
    
    @api.onchange('product_id')
    def prod_desc_name(self):
        self.prod_desc = self.product_id.name