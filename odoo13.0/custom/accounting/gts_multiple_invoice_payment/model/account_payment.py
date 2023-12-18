# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
# import odoo.addons.decimal_precision as dp


class PaymentInvoiceLine(models.Model):
    _name = 'payment.invoice.line'

    invoice_id = fields.Many2one('account.move', 'Invoice')
    payment_id = fields.Many2one('account.payment', 'Related Payment')
    move_line_id = fields.Many2one('account.move.line')
    partner_id = fields.Many2one(related='payment_id.partner_id', string='Partner')
    amount_total = fields.Float('Amount Total', digits=('Account'))
    residual = fields.Float('Amount Due', digits=('Account'))
    amount = fields.Float('Amount To Pay', digits=('Account'),
        help="Enter amount to pay for this invoice, supports partial payment")
    date_invoice = fields.Date('Invoice Date')
    select = fields.Boolean('Select', help="Click to select the invoice")
    untaxed_amount = fields.Float('Untaxed Amount', digits=('Account'))
    amount_tax = fields.Float('Tax', digits=('Account'))
    check_amount = fields.Float('Check Amount', digits=('Account'),
                                compute="compute_check_amount", store=True,)
    wt_rate = fields.Float('WT', digits=('Account'),
                        compute="compute_wt_rate", store=True,)

    
    @api.constrains('amount')
    def _check_amount(self):
        for line in self:
            if line.amount < 0:
                raise UserError(_('Amount to pay can not be less than 0! (Invoice code: %s)')
                    % line.invoice_id.number)
            if line.amount > line.residual:
                raise UserError(_('"Amount to pay" can not be greater than "Amount '
                                  'Due" ! (Invoice code: %s)')
                                % line.invoice_id.number)

    @api.onchange('invoice_id')
    def onchange_invoice(self):
        if self.invoice_id:
            # self.amount_total = self.invoice_id.amount_net_pay
            self.amount_total = self.invoice_id.amount_total
            coeff_net = self.invoice_id.amount_residual / self.invoice_id.amount_total
            self.residual = self.invoice_id.amount_total * coeff_net
        else:
            self.amount_total = 0.0
            self.residual = 0.0

    @api.onchange('select')
    def onchange_select(self):
        if self.invoice_id.amount_residual and self.invoice_id.amount_total:
            if self.select:
                #coeff_net = self.invoice_id.residual / self.invoice_id.amount_total
                self.amount = self.invoice_id.amount_residual
                # self.amount = self.invoice_id.amount_net_pay
            else:
                self.amount = 0.0
        else:
            if self.select:
                self.amount = self.residual
                self.check_amount = self.amount
            else:
                self.amount = 0.0
            
        

    # <-- START Code added by Srikesh Infotech for Calculate WT based on selected withholding tax rate
    # If tax = 0.00, then WT = [((Amount to pay) * WT Rate)] Eg: (500 * 0.01) = 5
    # If tax > 0.00, then WT = [((Amount to pay / 1.12) * WT Rate)] Eg: ((50/1.12) * 0.01) = 0.45
    #
    #Dats: removed depends
    @api.depends('amount','payment_id.tax_id')
    def compute_wt_rate(self):
        self.wt_rate = 0
        for line in self:
            if line.invoice_id:
                tax_val = line.payment_id.tax_id.amount
                vat = (tax_val / 100)
                if line.amount_tax:
                    if line.amount > 0:
                        wt =((line.amount/1.12) * vat)
                        line.update({'wt_rate':wt})
                else:
                    if line.amount > 0:
                        wt = (line.amount * vat)
                        line.update({'wt_rate':wt})
                        
            if line.move_line_id:
                tax_val = line.payment_id.tax_id.amount
                vat = (tax_val / 100)
                if line.amount_tax:
                    if line.amount > 0:
                        wt =((line.amount/1.12) * vat)
                        line.update({'wt_rate':wt})
                else:
                    if line.amount > 0:
                        wt = (line.amount * vat)
                        line.update({'wt_rate':wt})

    # ENDED calculate WT -->
    
    # <-- START Code added by Srikesh Infotech for Calculate Check Amount
    # Check Amount = (Amount to pay - WT)
    # Eg: check Amount = (500 - 5) = 495
    #Dats: remove depends
    @api.depends('amount','wt_rate')
    def compute_check_amount(self):
        for line in self:
            self.check_amount = 0
            if line.invoice_id:
                if line.amount > 0:
                    checkamount = (line.amount - line.wt_rate)
                    line.update({'check_amount':checkamount})
                    
            if line.select :
                line.update({'check_amount':line.amount})

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    invoice_total = fields.Float('Invoice Total', digits=('Account'),
        help="Shows total invoice amount selected for this payment")
    invoice_lines = fields.One2many('payment.invoice.line', 'payment_id', 'Invoices',
        help='Please select invoices for this partner for the payment')
    selected_inv_total = fields.Float(compute='compute_selected_invoice_total',
        store=True, string='Assigned Amount', digits=('Account'))
    balance = fields.Float(compute='_compute_balance', string='Balance', store=True,)
    manual_selection = fields.Boolean('Manual Selection?', digits=('Account'),
                                help="Click if you want to select the invoices manually")

    @api.depends('invoice_lines', 'invoice_lines.amount', 'amount')
    def _compute_balance(self):
        for payment in self:
            total = 0.0
            for line in payment.invoice_lines:
                total += line.amount
            if payment.amount >= total:
                balance = payment.amount - total
            else:
                balance = payment.amount - total
            payment.balance = balance


    @api.depends('invoice_lines', 'invoice_lines.amount', 'amount')
    def compute_selected_invoice_total(self):
        for payment in self:
            total = 0.0
            for line in payment.invoice_lines:
                total += line.amount
            payment.selected_inv_total = total
                  
    @api.onchange('partner_id', 'payment_type')
    def onchange_partner_id(self):
        Invoice = self.env['account.move']
        PaymentLine = self.env['payment.invoice.line']
        AccountMoveLine = self.env['account.move.line']
       
        if self.partner_id:
            partners_list = self.partner_id.child_ids.ids
            partners_list.append(self.partner_id.id)
            line_ids = []
            type = ''
            if self.payment_type == 'outbound':
                type = 'in_invoice'
            elif self.payment_type == 'inbound':
                type = 'out_invoice'
                #Dats: fixed conditions to select invoices
            invoices = Invoice.search([('partner_id', 'in', partners_list),
                ('state', 'in', ('posted', )), ('invoice_payment_state', '=', 'not_paid'), ('type', '=', type)])
            #  <-- START Code Added by Srikesh Infotech for added journal entries in payment invoice line
            if type == 'out_invoice':
                AccountMoveLine = self.env['account.move.line'].search([('is_select', '=',True),
                                                                ('partner_id','=',self.partner_id.id),
                                                                ('account_id.internal_type','=','receivable'),
                                                                ('reconciled','=',False)])
            elif type == 'in_invoice':
                AccountMoveLine = self.env['account.move.line'].search([('is_select', '=',True),
                                                                ('partner_id','=',self.partner_id.id),
                                                                ('account_id.internal_type','=','payable'),
                                                                ('reconciled','=',False)])
            # END code Added by Srikesh Infotech added journal entries in payment invoice line -->   
            # total_amount = 0
            # if self.amount > 0:
            #     total_amount = self.amount
            for invoice in invoices:
                # assigned_amount = 0
                # if total_amount > 0:
                #     if invoice.residual < total_amount:
                #         assigned_amount = invoice.residual
                #         total_amount -= invoice.residual
                #     else:
                #         assigned_amount = total_amount
                #         total_amount = 0
                
                coeff_net = invoice.amount_residual / invoice.amount_total  if invoice.amount_total != 0 else 0
                data = {
                    'invoice_id': invoice.id,
                    'amount_total': invoice.amount_total,
                    'residual':  invoice.amount_total * 1,
                    'amount': 0.0,
                    'date_invoice': invoice.invoice_date, #Dats: fixed key error
                    'untaxed_amount': invoice.amount_untaxed,
                    'amount_tax': invoice.amount_tax
                }
                
            
                line = PaymentLine.create(data)
                line_ids.append(line.id)
                
                # line_data.append((0, 0, data))
#  <-- START Code Added by Srikesh Infotech for added journal entries in payment invoice line
            for newline_id in AccountMoveLine:
                total_amt = abs(newline_id.debit - newline_id.credit)
                move_id = newline_id.move_id
                if  not newline_id.invoice_id :
                    if newline_id.amount_residual:
                        amount_residual = abs(newline_id.amount_residual)
                        coeff_net = amount_residual / total_amt
                    else:
                        coeff_net = total_amt / total_amt
                    if newline_id.move_id.state == 'posted' :
                        data = {
                            'move_line_id': newline_id.id,
                            'amount_total': total_amt,
                            'residual': (total_amt * coeff_net) ,
                            'amount': 0.0,
                            'date_invoice': newline_id.move_id.date,
                            'untaxed_amount': total_amt,
                        }
                        payment_line = PaymentLine.create(data)
                        line_ids.append(payment_line.id)
    # END code Added by Srikesh Infotech added journal entries in payment invoice line -->   
            self.invoice_lines = [(6, 0, line_ids)]
        else:
            if self.invoice_lines:
                for line in self.invoice_lines:
                    line.unlink()
            self.invoice_lines = []

    @api.onchange('invoice_lines', 'manual_selection')
    def onchange_invoice_lines(self):
        if self.invoice_lines:
            total = 0.0
            for line in self.invoice_lines:
                total += line.amount
            self.invoice_total = total
        else:
            self.invoice_total = 0.0
            self.amount = 0.0
        if self.manual_selection:
            total = 0.0
            for line in self.invoice_lines.filtered(lambda l: l.select):
                total += line.amount
            self.amount = total

    @api.onchange('amount')
    def onchange_amount(self):
        ''' Function to reset/select invoices on the basis of invoice date '''
        if self.amount > 0 and not self.manual_selection:
            total_amount = self.amount
            for line in self.invoice_lines:
                if total_amount > 0:
                    if line.residual < total_amount:
                        line.select = True
                        line.amount = line.residual
                        total_amount -= line.residual
                    else:
                        line.select = True
                        line.amount = total_amount
                        total_amount = 0
                else:
                    line.select = False
                    line.amount = 0
        if (self.amount <= 0):
            for line in self.invoice_lines:
                line.select = False
                line.amount = 0.0

    
    @api.constrains('amount', 'invoice_lines')
    def _check_invoice_amount(self):
        ''' Function to validate if user has selected more amount invoices than payment '''
        for payment in self:
            total = 0.0
            if payment.invoice_lines:
                for line in payment.invoice_lines:
                    total += line.amount
                if total > payment.amount:
                    raise UserError(_('You cannot select more value invoices than the payment amount'))

#  <-- Code Commented by Srikesh Infotech for _create_payment_entry method merged tax_payment_journal addon.
#     def _create_payment_entry(self, amount):
#         """ Create a journal entry corresponding to a payment, if the payment references invoice(s) they are reconciled.
#             Return the journal entry.
#             OVERRIDDEN: generated multiple journal items for each selected invoice
#         """
#         aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
#         invoice_currency = False
#         if self.invoice_ids and all([x.currency_id == self.invoice_ids[0].currency_id for x in self.invoice_ids]):
#             # if all the invoices selected share the same currency, record the paiement in that currency too
#             invoice_currency = self.invoice_ids[0].currency_id
#         debit, credit, amount_currency, currency_id = aml_obj.with_context(
#             date=self.payment_date).compute_amount_fields(
#             amount, self.currency_id, self.company_id.currency_id, invoice_currency)
# 
#         move = self.env['account.move'].create(self._get_move_vals())
#         # Custom Code
#         counterpart_aml = False
#         invoice_reconcile_amount = 0
#         sum_credit, sum_debit = 0, 0
#         invoice_dict = {}
#         # Creating invoice wise move lines
#         if self.invoice_lines:
#             for line in self.invoice_lines:
#                 if line.amount > 0:
#                     inv = line.invoice_id
#                     inv_amount = line.amount * (self.payment_type in ('outbound', 'transfer') and 1 or -1)
#                     invoice_currency = inv.currency_id
#                     debit1, credit1, amount_currency1, currency_id1 = aml_obj.with_context(
#                         date=self.payment_date).compute_amount_fields(
#                         inv_amount, self.currency_id, self.company_id.currency_id, invoice_currency)
#                     counterpart_aml_dict1 = self._get_shared_move_line_vals(
#                         debit1, credit1, amount_currency1, move.id, False)
#                     counterpart_aml_dict1.update(
#                         self._get_counterpart_move_line_vals(False))
#                     counterpart_aml_dict1.update({'currency_id': currency_id1})
#                     counterpart_aml1 = aml_obj.create(counterpart_aml_dict1)
#                     invoice_dict[counterpart_aml1] = inv
#                     # inv.register_payment(counterpart_aml1)
#                     invoice_reconcile_amount += inv_amount
#                     sum_credit += credit1
#                     sum_debit += debit1
#             # Creating journal item for remaining payment amount
#             remaining_amount = 0
#             if self.payment_type in ('outbound', 'transfer'):
#                 remaining_amount = amount - invoice_reconcile_amount
#             else:
#                 remaining_amount = invoice_reconcile_amount - amount
#             if remaining_amount > 0:
#                 remaining_amount = remaining_amount * (
#                         self.payment_type in ('outbound', 'transfer') and 1 or -1)
#                 debit1, credit1, amount_currency1, currency_id1 = aml_obj.with_context(
#                     date=self.payment_date).compute_amount_fields(
#                     remaining_amount, self.currency_id, self.company_id.currency_id, invoice_currency)
#                 counterpart_aml_dict1 = self._get_shared_move_line_vals(
#                     debit1, credit1, amount_currency1, move.id, False)
#                 counterpart_aml_dict1.update(
#                     self._get_counterpart_move_line_vals(False))
#                 counterpart_aml_dict1.update({'currency_id': currency_id1})
#                 counterpart_aml1 = aml_obj.create(counterpart_aml_dict1)
#                 sum_credit += credit1
#                 sum_debit += debit1
#             # Creating move line for currency exchange/conversion rate difference
#             if self.payment_type in ('outbound', 'transfer'):
#                 amount_diff = debit - sum_debit
#             else:
#                 amount_diff = credit - sum_credit
#             if amount_diff > 0:
#                 conversion = self._get_shared_move_line_vals(0, 0, 0, move.id, False)
#                 debit_co, credit_co, amount_currency_co, currency_id_co = aml_obj.with_context(
#                     date=self.payment_date).compute_amount_fields(
#                     amount_diff, self.currency_id, self.company_id.currency_id, invoice_currency)
# 
#                 conversion['name'] = _('Currency exchange rate difference')
#                 conversion['account_id'] = amount_diff > 0 and \
#                                            self.company_id.currency_exchange_journal_id.default_debit_account_id.id or \
#                                            self.company_id.currency_exchange_journal_id.default_credit_account_id.id
#                 if self.payment_type in ('outbound', 'transfer'):
#                     conversion['debit'] = amount_diff
#                     conversion['credit'] = 0
#                 else:
#                     conversion['debit'] = 0
#                     conversion['credit'] = amount_diff
#                 conversion['currency_id'] = currency_id_co
#                 conversion['payment_id'] = self.id
#                 aml_obj.create(conversion)
#             # for key,val in invoice_dict.items():
#             #     val.register_payment(key)
#         else:
#             # Default code
#             # Write line corresponding to invoice payment
#             counterpart_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, move.id, False)
#             counterpart_aml_dict.update(self._get_counterpart_move_line_vals(self.invoice_ids))
#             counterpart_aml_dict.update({'currency_id': currency_id})
#             counterpart_aml = aml_obj.create(counterpart_aml_dict)
#             self.invoice_ids.register_payment(counterpart_aml)
# 
#         # Default code
#         # Reconcile with the invoices
#         if self.payment_difference_handling == 'reconcile' and self.payment_difference:
#             writeoff_line = self._get_shared_move_line_vals(0, 0, 0, move.id, False)
#             debit_wo, credit_wo, amount_currency_wo, currency_id = aml_obj.with_context(
#                 date=self.payment_date).compute_amount_fields(
#                 self.payment_difference, self.currency_id, self.company_id.currency_id, invoice_currency)
#             writeoff_line['name'] = _('Counterpart')
#             writeoff_line['account_id'] = self.writeoff_account_id.id
#             writeoff_line['debit'] = debit_wo
#             writeoff_line['credit'] = credit_wo
#             writeoff_line['amount_currency'] = amount_currency_wo
#             writeoff_line['currency_id'] = currency_id
#             writeoff_line = aml_obj.create(writeoff_line)
#             if counterpart_aml['debit']:
#                 counterpart_aml['debit'] += credit_wo - debit_wo
#             if counterpart_aml['credit']:
#                 counterpart_aml['credit'] += debit_wo - credit_wo
#             counterpart_aml['amount_currency'] -= amount_currency_wo
#         # Write counterpart lines
#         if not self.currency_id != self.company_id.currency_id:
#             amount_currency = 0
#         liquidity_aml_dict = self._get_shared_move_line_vals(credit, debit, -amount_currency, move.id, False)
#         liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amount))
#         aml_obj.create(liquidity_aml_dict)
#         move.post()
#         for key, val in invoice_dict.items():
#             val.register_payment(key)
#         return move

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        default.update(invoice_lines=[], invoice_total=0.0)
        return super(AccountPayment, self).copy(default)
    
#    
