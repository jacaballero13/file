from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    sale_order = fields.Many2one('sale.order', string="Sale Order", domain=[('type', '=', 'out_refund')])
    
    state = fields.Selection(selection_add=[('waiting', 'Waiting for Approval'),
                                            ('approve_actng', 'Approved by Accounting'),
                                            ('approve', 'Approved by Admin')])
    

    def button_approve(self):
        return self.update({'state': 'approve_actng'})

    def button_approve1(self):
        return self.update({'state': 'approve'})

    def button_reject(self):
        return self.button_cancel()