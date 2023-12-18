# # -*- coding: utf-8 -*-
# from odoo import models, fields, api, _
# # from odoo.addons import decimal_precision as dp

# MAP_INVOICE_TYPE_PARTNER_TYPE = {
#     'out_invoice': 'customer',
#     'out_refund': 'customer',
#     'in_invoice': 'supplier',
#     'in_refund': 'supplier',
# }

# class AccountRegisterPayments(models.TransientModel):
#     _inherit = 'account.payment.register'
#     _description = "Register payments on multiple invoices"
    
#     tax_id = fields.Many2one('account.tax', string='Withholding Tax Rate')
    
#     tax_amount = fields.Float('Withholding Tax Amount',compute="multi_tax_calculate",digits=('Product Price'), store=True,)
    
#     tax_type = fields.Char('Tax categ',compute="get_multitax_type", store=True,)
    
#     check_amount = fields.Float(string='Check Amount', digits=('Product Price'),
#                                 compute="get_multi_check_amount", store=True,)
    
#     check_amount_in_word = fields.Char(string="Check Amount(in words)", compute="get_multi_check_amount_in_word", store=True,)
    

#     @api.depends('journal_id')
#     def get_multitax_type(self):
#         if self.partner_type =='customer':
#             self.tax_type ='sale'
#         if self.partner_type =='supplier':
#             self.tax_type ='purchase'
#         if self.partner_type ==False:
#             active_ids = self._context.get('active_ids')
#             invoices = self.env['account.move'].browse(active_ids)
#             if MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].move_type] =='customer':
#                 self.tax_type ='sale'
#             if MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].move_type] =='supplier':
#                 self.tax_type ='purchase'
            
#     @api.depends('tax_id','amount')
#     def multi_tax_calculate(self):
#         # <-- START Code Added by Srikesh Infotech for calculate withholding tax amount
#         tax_amount = 0
#         tax_val = self.tax_id.amount
#         vat = (tax_val / 100)
#         active_ids = self._context.get('active_ids')
#         invoices = self.env['account.move'].browse(active_ids)
#         if self.amount > 0:
#             total_amount = self.amount
#             for invoice in invoices:
#                 if total_amount > 0:
#                     if invoice.amount_residual < total_amount:
#                         if invoice.amount_tax:
#                             tax_amount +=((invoice.amount_residual/1.12) * vat)
#                         else:
#                             tax_amount += (invoice.amount_residual * vat)
#                         total_amount -= invoice.amount_residual
#                     else:
#                         if invoice.amount_tax:
#                             tax_amount +=((total_amount/1.12) * vat)
#                         else:
#                             tax_amount += (total_amount * vat)
#                         total_amount = 0
#         self.tax_amount = tax_amount
#     # END code Added by Srikesh Infotech for calculate withholding tax amount -->    

#     #  <-- START Code added by Srikesh Infotech for convert check amount to word
#     @api.depends('check_amount')
#     def get_multi_check_amount_in_word(self):
#         amount_word = self.currency_id.amount_to_text(self.check_amount)
#         self.check_amount_in_word =amount_word
#     # ENDED convert check amount to word -->
    
#     # <-- START Code added by Srikesh Infotech for calculate check amount value
#     # (Payment Amount - Withholding Tax Amount)
#     @api.depends('amount','tax_amount')
#     def get_multi_check_amount(self):
#         amount = self.amount
#         tax_amount = self.tax_amount        
#         check_amount =(amount - float(tax_amount))
#         self.check_amount = check_amount
#     # ENDED calculate check amount value -->
    
    
    
#     def _prepare_payment_vals(self, invoices):
#         '''Create the payment values.

#         :param invoices: The invoices that should have the same commercial partner and the same type.
#         :return: The payment values as a dictionary.
#         '''
#         res = super(AccountRegisterPayments, self)._prepare_payment_vals(invoices)
#         res.update({
#             'tax_id': self.tax_id.id,
#             'tax_amount': self.tax_amount,
#         })
#         return res
    
    
#     def create_payments(self):
#         '''Create payments according to the invoices.
#         Having invoices with different commercial_partner_id or different type (Vendor bills with customer invoices)
#         leads to multiple payments.
#         In case of all the invoices are related to the same commercial_partner_id and have the same type,
#         only one payment will be created.

#         :return: The ir.actions.act_window to show created payments.
#         '''
#         Payment = self.env['account.payment']
#         PaymentLine = self.env['payment.invoice.line']
#         payments = Payment
#         payment_id = Payment
#         line_ids = []
#         amount = 0
#         for payment_vals in self.get_payments_vals():
#             payment_id = Payment.create(payment_vals)
#             payments += payment_id
#             amount = payment_vals.get('amount')
#             if payment_vals.get('invoice_ids'):
#                 invoice_ids = payment_vals.get('invoice_ids')[0][2]
#                 acc_invoice = self.env['account.move'].search([('id','in',invoice_ids)])
#                 for invoice in acc_invoice:
#                     coeff_net = invoice.amount_residual / invoice.amount_total
#                     data = {
#                         'invoice_id': invoice.id,
#                         'amount_total': invoice.amount_total,
#                         'residual':  invoice.amount_total * coeff_net,
#                         'amount': 0.0,
#                         'date_invoice': invoice.invoice_date,
#                         'untaxed_amount': invoice.amount_untaxed,
#                         'amount_tax': invoice.amount_tax,
#                         'payment_id':payment_id.id
#                     }
#                     line = PaymentLine.create(data)
#                     line_ids.append(line.id)
#                 payment_id.invoice_lines = [(6, 0, line_ids)]
#                 payment_id.onchange_amount()
#                 line_ids = []
#         payments.post()
#         return {
#             'name': _('Payments'),
#             'domain': [('id', 'in', payments.ids), ('state', '=', 'posted')],
#             'view_type': 'form',
#             'view_mode': 'tree,form',
#             'res_model': 'account.payment',
#             'view_id': False,
#             'type': 'ir.actions.act_window',
#         }