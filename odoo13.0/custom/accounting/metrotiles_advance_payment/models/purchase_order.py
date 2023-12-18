# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import Warning

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    payment_history_ids = fields.One2many('payment.history.purchase','purchase_id', string="Advanvce Payment Information")
    # payment_history_ids = fields.One2many('purchase.advance.payment', 'purchase_id',
    #                                       string="Advanvce Payment Information")


    def set_purchase_advance_payment(self):
        view_id = self.env.ref('metrotiles_advance_payment.purchase_advance_payment_wizard')
        if view_id:
            pay_wiz_data={
                'name' : _('Purchase Advance Payment'),
                'type' : 'ir.actions.act_window',
                'view_type' : 'form',
                'view_mode' : 'form',
                'res_model' : 'purchase.advance.payment',
                'view_id' : view_id.id,
                'target' : 'new',
                'context' : {
                            'name':self.name,
                            'order_id':self.id,
                            'total_amount':self.amount_total,
                            'company_id':self.company_id.id,
                            'currency_id':self.currency_id.id,
                            'date_order':self.date_order,
                            'partner_id':self.partner_id.id,
                             },
            }
        return pay_wiz_data