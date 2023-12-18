# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, models,_
from odoo.exceptions import UserError


class report_check_voucher(models.AbstractModel):
    _name = 'report.gts_multiple_invoice_payment.report_check_voucher'

    @api.model
    def _get_report_values(self, docids, context=None,data=None):
        models = self.env['account.payment']
        payment_dict = {}
        account_payment = []
        for payment_id in docids:
            debit = 0
            credit = 0
            account_payment_line = []
            account_payment_id = models.search([('id', '=', payment_id)])
            account_payment.append(account_payment_id)
            account_move = self.env['account.move'].search([('name','=',account_payment_id.move_name)])
            account_move_line = self.env['account.move.line'].search([('move_id','=',account_move.id)])
            account_payment_line.append(account_move_line)
            for line in account_move_line:
                debit = debit + line.debit
                credit = credit + line.credit
            payment_dict[account_payment_id.id] = account_payment_line
            payment_dict['credit'+str(account_payment_id.id)] = credit
            payment_dict['debit'+str(account_payment_id.id)] = debit
        data = {
                   'doc_ids': docids,
                   'doc_model': models,
                   'docs': account_payment,
                   'payment_dict': payment_dict,
            }
        return data
