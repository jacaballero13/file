# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime

class AccountPayment(models.Model):
    _inherit = 'account.payment'
    
    
    @api.model
    def create(self, vals):
        res = super(AccountPayment,self).create(vals)
        branch_id = vals.get('branch_id', None)
        current_date=datetime.now()
        if branch_id:
            branch_prefix = self.env['res.branch'].search([('id','=',branch_id)])
            if res.payment_type == 'inbound':
                if branch_prefix:
                    sequence = self.env['ir.sequence'].search([('code','=','account.payment.customer.invoice')])
                    sequence.update({'prefix': '%s/%s/%s/'%("CUST.IN", branch_prefix.branch_sequence,current_date.year)})
                    
                if not branch_prefix.branch_sequence:
                    raise UserError('Branch sequence must be set.')
                    

            if res.payment_type == 'outbound':
                if branch_prefix:
                    sequence = self.env['ir.sequence'].search([('code','=','account.payment.supplier.invoice')])
                    sequence.update({'prefix': '%s/%s/%s/'%("BILL" ,branch_prefix.branch_sequence,current_date.year)})
                    
                if not branch_prefix.branch_sequence:
                    raise UserError('Branch sequence must be set.')
        return res

    # Call sequence method if branch change by user
    # def post(self):
    #     for rec in self:
    #         if rec.state == 'draft' and rec.name:
    #             # Use the right sequence to set the name
    #             if rec.payment_type == 'transfer':
    #                 sequence_code = 'account.payment.transfer'
    #             else:
    #                 if rec.partner_type == 'customer':
    #                     if rec.payment_type == 'inbound':
    #                         sequence_code = 'account.payment.customer.invoice'
    #                     if rec.payment_type == 'outbound':
    #                         sequence_code = 'account.payment.customer.refund'
    #                 if rec.partner_type == 'supplier':
    #                     if rec.payment_type == 'inbound':
    #                         sequence_code = 'account.payment.supplier.refund'
    #                     if rec.payment_type == 'outbound':
    #                         sequence_code = 'account.payment.supplier.invoice'
    #             rec.name = self.env['ir.sequence'].next_by_code(sequence_code, sequence_date=rec.payment_date)
    #     return super(AccountPayment, self).post()

    # def write(self, vals):
    #     res = super(AccountPayment,self).write(vals)
    #     branch_id = self.branch_id.id
    #     current_date = datetime.now()
    #     branch_prefix = self.env['res.branch'].search([('id',' =', branch_id)])
    #     for rec in self:
    #         if rec.state == 'draft':
    #             if branch_id:
    #                 if rec.payment_type == 'inbound':
    #                     if branch_prefix:
    #                         sequence = self.env['ir.sequence'].search([('code', '=', 'account.payment.customer.invoice')])
    #                         sequence.update({'prefix': '%s/%s/%s/' % ("CUST.IN", branch_prefix.branch_sequence,current_date.year)})
    #                     if not branch_prefix.branch_sequence:
    #                         raise UserError('Branch sequence must be set.')
    #                 if rec.payment_type == 'outbound':
    #                     if branch_prefix:
    #                         sequence = self.env['ir.sequence'].search([('code','=','account.payment.supplier.invoice')])
    #                         sequence.update({'prefix': '%s/%s/%s/'%("BILL" ,branch_prefix.branch_sequence,current_date.year)})
    #                     if not branch_prefix.branch_sequence:
    #                         raise UserError('Branch sequence must be set.')
    #     return res
