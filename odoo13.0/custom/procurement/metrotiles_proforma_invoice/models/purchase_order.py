# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import Warning

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    proforma_ref = fields.Many2one('metrotiles_procurement.proforma_invoice', string='Proforma Invoice No.', tracking=True)
    
    proforma_invoice_count = fields.Integer(string='Proforma Invoices', compute='get_proforma_invoice_count')

    def get_proforma_invoice_count(self):
        count = self.env['metrotiles_procurement.proforma_invoice'].search_count([('purchase_order_id', '=', self.id)])
        self.proforma_invoice_count = count

    # add open proforma invoice in smart button
    def action_open_proforma_invoice(self):
        view_id = self.env.ref('metrotiles_procurement.proforma_invoice_tree_view').id
        return {
            'name': _('Proforma Invoices'),
            'domain': [('purchase_order_id', '=', self.id)],
            'view_mode': 'form',
            'res_model': 'metrotiles_procurement.proforma_invoice',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }

    # call wizard to create pro-forma invoices
    def create_proforma_invoice(self):
        view_id = self.env.ref('metrotiles_proforma_invoice.mt_create_proforma_popup_wizard')
        if view_id:
            pf_wiz_data={
                'name' : _('Create Pro-Forma Invoice'),
                'type' : 'ir.actions.act_window',
                'view_type' : 'form',
                'view_mode' : 'form',
                'res_model' : 'mt_create.proforma_popup',
                'view_id' : view_id.id,
                'target' : 'new',
                'context' : {
                            'default_purchase_order_id':self.id,
                            'currency':self.currency_id.id,
                            'partner_id':self.partner_id.id,
                            },
            }
        return pf_wiz_data