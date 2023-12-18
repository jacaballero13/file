from odoo import models, fields, api, _
# from odoo.addons import decimal_precision as dp

class account_payment(models.Model):
    _inherit = "account.payment"
    
    tax_id = fields.Many2one('account.tax', string='Withholding Tax Rate')
    
    tax_amount = fields.Float('Withholding Tax Amount',compute="tax_calculate",digits=('Product Price'))
    
    tax_type = fields.Char('Tax categ',compute="get_tax_type")
    
    check_amount = fields.Float(string='Check Amount', digits=('Product Price'),
                                compute="get_check_amount")
    
    check_amount_in_word = fields.Char(string="Check Amount(in words)", compute="get_check_amount_in_word")
    
    @api.depends('journal_id')
    def get_tax_type(self):
        if self.partner_type =='customer':
            self.tax_type ='sale'
        if self.partner_type =='supplier':
            self.tax_type ='purchase'
        if self.partner_type ==False:
            self.tax_type ='none'
            
    @api.depends('tax_id','amount')
    def tax_calculate(self):
        # code commented by Srikesh Infotech       
        # if self.tax_id:
        #     self.tax_amount = ((self.amount*self.tax_id.amount)/100)
        
        # <-- START Code Added by Srikesh Infotech for calculate withholding tax amount
        tax_amount = 0
        if self.invoice_lines:
            for line in self.invoice_lines:
                if line.select:
                    tax_amount += (line.wt_rate)
        else:
            if self.amount > 0:
                tax_val = self.tax_id.amount
                vat = (tax_val / 100)
                active_ids = self._context.get('active_ids')
                if active_ids:
                    invoices = self.env['account.move'].browse(active_ids)
                    if invoices.amount_tax:
                        tax_amount =((self.amount/1.12) * vat)
                    else:
                        tax_amount = (self.amount * vat)
                else:
                    tax_amount = (self.amount * vat)
                
        self.tax_amount = tax_amount
         # END code Added by Srikesh Infotech for calculate withholding tax amount -->        
           
    def _create_payment_entry(self, amount):
        """ Create a journal entry corresponding to a payment, if the payment references invoice(s) they are reconciled.
            Return the journal entry.
        """
        total_amount  = amount
        aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
        move = self.env['account.move'].create(self._get_move_vals())
        PaymentLine = self.env['payment.invoice.line']
        invoice_currency = False
        invoice_payment = []
        amount_currency =0
        # Modified by  Srikesh Infotech payment entries will generated selected invoices.
        line_amount = 0
        counterpart_aml = False
        invoice_reconcile_amount = 0
        sum_credit, sum_debit = 0, 0
        sum_cr, sum_dr = 0, 0
        invoice_dict = {}
        bach_payment = []
        if not self.invoice_lines and not self.batch_payment_ids:
            if self.invoice_ids and all([x.currency_id == self.invoice_ids[0].currency_id for x in self.invoice_ids]):
                #if all the invoices selected share the same currency, record the paiement in that currency too
                invoice_currency = self.invoice_ids[0].currency_id
            debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.date).compute_amount_fields(amount, self.currency_id, self.company_id.currency_id, invoice_currency)
            tax = 0
            #custom method written for tax entry
            if self.tax_id:
                if self.payment_type =='inbound': 
                    tax = self.tax_amount
                    tax_aml_dict = self._get_shared_move_line_vals(tax, debit, -amount_currency, move.id, False)
                    tax_aml_dict.update(self._get_tax_move_line_vals(self.invoice_ids))
                    tax_aml_dict.update({'currency_id': currency_id})
                    tax_aml = aml_obj.create(tax_aml_dict)
                    
    #                 payable = credit - tax
                    counterpart_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, move.id, False)
                    counterpart_aml_dict.update(self._get_counterpart_move_line_vals(self.invoice_ids))
                    counterpart_aml_dict.update({'currency_id': currency_id})
                    if not self.invoice_ids:
                        counterpart_aml_dict.update({'is_select': True})
                    counterpart_aml = aml_obj.create(counterpart_aml_dict)
                
                if self.payment_type =='outbound':
                    tax = self.tax_amount
                    tax_aml_dict = self._get_shared_move_line_vals(credit, tax, -amount_currency, move.id, False)
                    tax_aml_dict.update(self._get_tax_move_line_vals(self.invoice_ids))
                    tax_aml_dict.update({'currency_id': currency_id})
                    tax_aml = aml_obj.create(tax_aml_dict)
            
                             
    #                 receveable = debit - tax
                    counterpart_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, move.id, False)
                    counterpart_aml_dict.update(self._get_counterpart_move_line_vals(self.invoice_ids))
                    counterpart_aml_dict.update({'currency_id': currency_id})
                    if not self.invoice_ids:
                        counterpart_aml_dict.update({'is_select': True})
                    counterpart_aml = aml_obj.create(counterpart_aml_dict)
                
                if self.payment_type =='transfer':
                    tax =  0
            #Write line corresponding to invoice payment odoo method
            else:
                counterpart_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, move.id, False)
                counterpart_aml_dict.update(self._get_counterpart_move_line_vals(self.invoice_ids))
                counterpart_aml_dict.update({'currency_id': currency_id})
                if not self.invoice_ids:
                    counterpart_aml_dict.update({'is_select': True})
                counterpart_aml = aml_obj.create(counterpart_aml_dict)
                if self.payment_type =='transfer':
                    tax =  0
            #Write counterpart lines
            if not self.currency_id != self.company_id.currency_id:
                amount_currency = 0
                
    
            #custom code
            flag= 0
            if credit != 0:
                bank_credit = credit - tax
                liquidity_aml_dict = self._get_shared_move_line_vals(bank_credit, debit, -amount_currency, move.id, False)
                flag =1
            if debit!=0:
                bank_debit =  debit - tax
                liquidity_aml_dict = self._get_shared_move_line_vals(credit, bank_debit, -amount_currency, move.id, False)
                flag =1
                #end
            if flag ==0:
                liquidity_aml_dict = self._get_shared_move_line_vals(credit, debit, -amount_currency, move.id, False)
            liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amount))
            aml_obj.create(liquidity_aml_dict)
        else:
            for line in self.invoice_lines:
                if line.select:
                    line_amount += line.amount
                    if self.payment_type =='inbound':
                        amount = -line.amount
                    if self.payment_type =='outbound':
                         amount = line.amount
    
                    if line.invoice_id and all([x.currency_id == line.invoice_id.currency_id for x in line.invoice_id]):
                        #if all the invoices selected share the same currency, record the payment in that currency too
                        invoice_currency = line.invoice_id.currency_id
                    debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.date).compute_amount_fields(amount, self.currency_id, self.company_id.currency_id, invoice_currency)
                    sum_cr += credit
                    sum_dr += debit
                    inv_amount = line.amount * (self.payment_type in ('outbound', 'transfer') and 1 or -1)
                    currency = self.currency_id
                    debit1, credit1, amount_currency1, currency_id1 = aml_obj.with_context(
                            date=self.date).compute_amount_fields(
                            inv_amount, self.currency_id, self.company_id.currency_id, currency)
                    invoice_reconcile_amount += inv_amount
                    sum_credit += credit1
                    sum_debit += debit1
                    tax = 0
                    #custom method written for tax entry
                    if self.tax_id:
                        if self.payment_type =='inbound':
                            # <-- STARED Added Srikesh Infotech for set tax = withhold tax amount
                            tax = line.wt_rate
                            # ENDED Added Srikesh Infotech for set tax = withhold tax amount -->
                            #Commented by Srikesh Infotech
                            #tax =  round(((credit*self.tax_id.amount)/100)) 
            #                 tax =  (((credit*self.tax_id.amount)/100))
            
                            tax_aml_dict = self._get_shared_move_line_vals(tax, debit, -amount_currency, move.id, False)
                            tax_aml_dict.update(self._get_tax_move_line_vals(line.invoice_id))
                            tax_aml_dict.update({'currency_id': currency_id})
                            tax_aml = aml_obj.create(tax_aml_dict)
                            
            #                 payable = credit - tax
                            counterpart_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, move.id, False)
                            counterpart_aml_dict.update(self._get_counterpart_move_line_vals(line.invoice_id))
                            counterpart_aml_dict.update({'currency_id': currency_id})
                            counterpart_aml = aml_obj.create(counterpart_aml_dict)
                        
                        if self.payment_type =='outbound':
                            #Commented by Srikesh Infotech
                            #tax =  ((debit*self.tax_id.amount)/100)
                            # <-- STARED Added Srikesh Infotech for set tax = withhold tax amount
                            tax = line.wt_rate
                            # ENDED Added Srikesh Infotech for set tax = withhold tax amount -->
                            tax_aml_dict = self._get_shared_move_line_vals(credit, tax, -amount_currency, move.id, False)
                            tax_aml_dict.update(self._get_tax_move_line_vals(line.invoice_id))
                            tax_aml_dict.update({'currency_id': currency_id})
                            tax_aml = aml_obj.create(tax_aml_dict)
                            
                                     
            #                 receveable = debit - tax
                            counterpart_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, move.id, False)
                            counterpart_aml_dict.update(self._get_counterpart_move_line_vals(line.invoice_id))
                            counterpart_aml_dict.update({'currency_id': currency_id})
                            counterpart_aml = aml_obj.create(counterpart_aml_dict)
                        
                        if self.payment_type =='transfer':
                            tax =  0
                    #Write line corresponding to invoice payment odoo method
                    else:
                        counterpart_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, move.id, False)
                        counterpart_aml_dict.update(self._get_counterpart_move_line_vals(line.invoice_id))
                        counterpart_aml_dict.update({'currency_id': currency_id})
                        counterpart_aml = aml_obj.create(counterpart_aml_dict)
                        if self.payment_type =='transfer':
                            tax =  0
    
                    #Reconcile with the invoices
                    if self.payment_difference_handling == 'reconcile' and self.payment_difference:
                        writeoff_line = self._get_shared_move_line_vals(0, 0, 0, move.id, False)
                        amount_currency_wo, currency_id = aml_obj.with_context(date=self.date).compute_amount_fields(self.payment_difference, self.currency_id, self.company_id.currency_id, invoice_currency)[2:]
                        # the writeoff debit and credit must be computed from the invoice residual in company currency
                        # minus the payment amount in company currency, and not from the payment difference in the payment currency
                        # to avoid loss of precision during the currency rate computations. See revision 20935462a0cabeb45480ce70114ff2f4e91eaf79 for a detailed example.
                        total_residual_company_signed = sum(invoice.residual_company_signed for invoice in self.invoice_ids)
                        total_payment_company_signed = self.currency_id.with_context(date=self.date).compute(self.amount, self.company_id.currency_id)
                        if self.invoice_ids[0].type in ['in_invoice', 'out_refund']:
                            amount_wo = total_payment_company_signed - total_residual_company_signed
                        else:
                            amount_wo = total_residual_company_signed - total_payment_company_signed
                        # Align the sign of the secondary currency writeoff amount with the sign of the writeoff
                        # amount in the company currency
                        if amount_wo > 0:
                            debit_wo = amount_wo
                            credit_wo = 0.0
                            amount_currency_wo = abs(amount_currency_wo)
                        else:
                            debit_wo = 0.0
                            credit_wo = -amount_wo
                            amount_currency_wo = -abs(amount_currency_wo)
                        writeoff_line['name'] = _('Counterpart')
                        writeoff_line['account_id'] = self.writeoff_account_id.id
                        writeoff_line['debit'] = debit_wo
                        writeoff_line['credit'] = credit_wo
                        writeoff_line['amount_currency'] = amount_currency_wo
                        writeoff_line['currency_id'] = currency_id
                        writeoff_line = aml_obj.create(writeoff_line)
                        if counterpart_aml['debit']:
                            counterpart_aml['debit'] += credit_wo - debit_wo
                        if counterpart_aml['credit']:
                            counterpart_aml['credit'] += debit_wo - credit_wo
                        counterpart_aml['amount_currency'] -= amount_currency_wo
            #         self.invoice_ids.register_payment(counterpart_aml)
            
                    #Write counterpart lines
                    if not self.currency_id != self.company_id.currency_id:
                        amount_currency = 0
                        
            
                    #custom code
                    flag= 0
                    if credit != 0:
                        bank_credit = credit - tax
                        liquidity_aml_dict = self._get_shared_move_line_vals(bank_credit, debit, -amount_currency, move.id, False)
                        flag =1
                    if debit!=0:
                        bank_debit =  debit - tax
                        liquidity_aml_dict = self._get_shared_move_line_vals(credit, bank_debit, -amount_currency, move.id, False)
                        flag =1
                        #end
                    if flag ==0:
                        liquidity_aml_dict = self._get_shared_move_line_vals(credit, debit, -amount_currency, move.id, False)
                    liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amount))
                    aml_obj.create(liquidity_aml_dict)
                    invoice_payment.append({'invoice_id':line.invoice_id.id,
                                      'move_line_id':counterpart_aml,
                                      'acc_move_line_id':line.move_line_id.id})
            for line in self.batch_payment_ids:
                line.update({'move_id':move.id})
                tax = line.wt_amount
                if self.payment_type =='outbound':
                    amount = line.gross_payable
                if self.invoice_ids and all([x.currency_id == self.invoice_ids[0].currency_id for x in self.invoice_ids]):
                #if all the invoices selected share the same currency, record the paiement in that currency too
                    invoice_currency = self.invoice_ids[0].currency_id
                debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.date).compute_amount_fields(amount, self.currency_id, self.company_id.currency_id, invoice_currency)
                sum_cr += credit
                sum_dr += debit
                inv_amount = line.gross_payable * (self.payment_type in ('outbound', 'transfer') and 1 or -1)
                currency = self.currency_id
                debit1, credit1, amount_currency1, currency_id1 = aml_obj.with_context(
                        date=self.date).compute_amount_fields(
                        inv_amount, self.currency_id, self.company_id.currency_id, currency)
                invoice_reconcile_amount += inv_amount
                sum_credit += credit1
                sum_debit += debit1
                if line.withhold_tax:
                    if self.payment_type_batch =='outbound':
                        tax = line.wt_amount
                        
        #                 payable = credit - tax
                        #debit = line.gross_payable
                        counterpart_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, move.id, False)
                        counterpart_aml_dict.update(self._get_counterpart_move_line_vals(False))
                        counterpart_aml_dict.update(self._get_counterpart_batch_move_line_vals(line))
                        counterpart_aml_dict.update({'currency_id': currency_id})
                        counterpart_aml = aml_obj.create(counterpart_aml_dict)
                        counterpart_aml.update({'isbatch_payment':True}) 
                else:
                    counterpart_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, move.id, False)
                    counterpart_aml_dict.update(self._get_counterpart_move_line_vals(self.invoice_ids))
                    counterpart_aml_dict.update(self._get_counterpart_batch_move_line_vals(line))
                    counterpart_aml_dict.update({'currency_id': currency_id})
                    counterpart_aml = aml_obj.create(counterpart_aml_dict)
                    counterpart_aml.update({'isbatch_payment':True})
                  #Reconcile with the invoices
                if self.payment_difference_handling == 'reconcile' and self.payment_difference:
                    writeoff_line = self._get_shared_move_line_vals(0, 0, 0, move.id, False)
                    amount_currency_wo, currency_id = aml_obj.with_context(date=self.date).compute_amount_fields(self.payment_difference, self.currency_id, self.company_id.currency_id, invoice_currency)[2:]
                    total_residual_company_signed = sum(invoice.residual_company_signed for invoice in self.invoice_ids)
                    total_payment_company_signed = self.currency_id.with_context(date=self.date).compute(self.amount, self.company_id.currency_id)
                    if self.invoice_ids[0].type in ['in_invoice', 'out_refund']:
                        amount_wo = total_payment_company_signed - total_residual_company_signed
                    else:
                        amount_wo = total_residual_company_signed - total_payment_company_signed
                    if amount_wo > 0:
                        debit_wo = amount_wo
                        credit_wo = 0.0
                        amount_currency_wo = abs(amount_currency_wo)
                    else:
                        debit_wo = 0.0
                        credit_wo = -amount_wo
                        amount_currency_wo = -abs(amount_currency_wo)
                    writeoff_line['name'] = self.writeoff_label
                    writeoff_line['account_id'] = self.writeoff_account_id.id
                    writeoff_line['debit'] = debit_wo
                    writeoff_line['credit'] = credit_wo
                    writeoff_line['amount_currency'] = amount_currency_wo
                    writeoff_line['currency_id'] = currency_id
                    writeoff_line = aml_obj.create(writeoff_line)
                    if counterpart_aml['debit'] or (writeoff_line['credit'] and not counterpart_aml['credit']):
                        counterpart_aml['debit'] += credit_wo - debit_wo
                    if counterpart_aml['credit'] or (writeoff_line['debit'] and not counterpart_aml['debit']):
                        counterpart_aml['credit'] += debit_wo - credit_wo
                    counterpart_aml['amount_currency'] -= amount_currency_wo
        
                #Write counterpart lines
                if not self.currency_id.is_zero(self.amount):
                    if not self.currency_id != self.company_id.currency_id:
                        amount_currency = 0
                    flag= 0
                    if credit != 0:
                        bank_credit = credit - tax
                        liquidity_aml_dict = self._get_shared_move_line_vals(bank_credit, debit, -amount_currency, move.id, False)
                        flag =1
                    if debit!=0:
                        bank_debit =  debit - tax
                        liquidity_aml_dict = self._get_shared_move_line_vals(credit, bank_debit, -amount_currency, move.id, False)
                        flag =1
                        #end
                    if flag ==0:
                        liquidity_aml_dict = self._get_shared_move_line_vals(credit, debit, -amount_currency, move.id, False)
                    liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amount))
                    liquidity_aml_dict.update(self._get_batch_move_line_vals(line))
                    aml_obj.create(liquidity_aml_dict)
                    aml_obj.update({'isbatch_payment':True})
                    if tax>0:
                        tax_aml_dict = self._get_shared_move_line_vals( credit,tax, -amount_currency, move.id, False)
                        tax_aml_dict.update(self._get_tax_move_line_vals(False))
                        tax_aml_dict.update(self._get_tax_wt_account(line))
                        
                        tax_aml_dict.update({'currency_id': currency_id})
                        tax_aml = aml_obj.create(tax_aml_dict)
                        tax_aml.update({'isbatch_payment':True})
                    bach_payment.append({'batch_id':line.id,
                                          'move_line_id':counterpart_aml,
                                          'acc_move_line_id':line.move_line_id.id})
            # Creating journal item for remaining payment amount
            remaining_amount = 0
            if self.payment_type in ('outbound', 'transfer'):
                remaining_amount = total_amount - invoice_reconcile_amount
            else:
                remaining_amount = invoice_reconcile_amount - total_amount
            if remaining_amount > 0:
                remaining_amount = remaining_amount * (
                        self.payment_type in ('outbound', 'transfer') and 1 or -1)
                debit1, credit1, amount_currency1, currency_id1 = aml_obj.with_context(
                    date=self.date).compute_amount_fields(
                    remaining_amount, self.currency_id, self.company_id.currency_id, invoice_currency)
                counterpart_aml_dict1 = self._get_shared_move_line_vals(
                    debit1, credit1, amount_currency1, move.id, False)
                counterpart_aml_dict1.update(
                    self._get_counterpart_move_line_vals(False))
                counterpart_aml_dict1.update({'currency_id': currency_id1})
                counterpart_aml1 = aml_obj.create(counterpart_aml_dict1)
                sum_cr += credit1
                sum_dr += debit1
                sum_credit += credit1
                sum_debit += debit1
                flag= 0
                if credit1 != 0:
                    bank_credit = credit1
                    liquidity_aml_dict1 = self._get_shared_move_line_vals(bank_credit, debit1, -amount_currency, move.id, False)
                    flag =1
                if debit1!=0:
                    bank_debit =  debit1
                    liquidity_aml_dict1 = self._get_shared_move_line_vals(credit1, bank_debit, -amount_currency, move.id, False)
                    flag =1
                    #end
                liquidity_aml_dict1.update(self._get_liquidity_move_line_vals(-remaining_amount))
                aml_obj.create(liquidity_aml_dict1)
                aml_obj.update({'isbatch_payment':True})
            # Creating move line for currency exchange/conversion rate difference
            if self.payment_type in ('outbound', 'transfer'):
                amount_diff = sum_dr - sum_debit
            else:
                amount_diff = sum_cr - sum_credit
            if amount_diff > 0:
                conversion = self._get_shared_move_line_vals(0, 0, 0, move.id, False)
                debit_co, credit_co, amount_currency_co, currency_id_co = aml_obj.with_context(
                    date=self.date).compute_amount_fields(
                    amount_diff, self.currency_id, self.company_id.currency_id, invoice_currency)
    
                conversion['name'] = _('Currency exchange rate difference')
                conversion['account_id'] = amount_diff > 0 and \
                                           self.company_id.currency_exchange_journal_id.default_debit_account_id.id or \
                                           self.company_id.currency_exchange_journal_id.default_credit_account_id.id
                if self.payment_type in ('outbound', 'transfer'):
                    conversion['debit'] = amount_diff
                    conversion['credit'] = 0
                else:
                    conversion['debit'] = 0
                    conversion['credit'] = amount_diff
                conversion['currency_id'] = currency_id_co
                conversion['payment_id'] = self.id
                aml_obj.create(conversion)
        move.post()
        if self.batch_payment_ids :
            move.update({'isbatch_payment':True})
        # Added by Srikesh infotech for Reconciliation of Journal Items should be automatic once payment is validated. 
        if self.invoice_lines:
            for line in self.invoice_lines:
                # Selected payment was reconciled.
                if line.select:
                    for payment in invoice_payment:
                        if(payment.get('invoice_id') == line.invoice_id.id and payment.get('invoice_id') != False):
                            line.invoice_id.register_payment(payment.get('move_line_id'))
                        elif(payment.get('acc_move_line_id') == line.move_line_id.id and payment.get('acc_move_line_id') != False):
                            self.journal_register_payment(payment.get('move_line_id'))

        else:
            self.invoice_ids.register_payment(counterpart_aml)
        if not self.invoice_lines:
            if self.invoice_ids:
                coeff_net = self.invoice_ids.residual / self.invoice_ids.amount_total
                data = {
                    'invoice_id': self.invoice_ids.id,
                    'amount_total': self.invoice_ids.amount_total,
                    'residual':  self.invoice_ids.amount_total * coeff_net,
                    'amount': 0.0,
                    'date_invoice': self.invoice_ids.date_invoice,
                    'untaxed_amount': self.invoice_ids.amount_untaxed,
                    'amount_tax': self.invoice_ids.amount_tax,
                    'payment_id':self.id
                }
                line = PaymentLine.create(data)
                self.onchange_amount()
        return move
    # Added by Srikesh infotech for Reconciliation of  Journal entries 
   
    def journal_register_payment(self, payment_line, writeoff_acc_id=False, writeoff_journal_id=False):
        """ Reconcile payable/receivable lines from the invoice with payment_line """
        line_to_reconcile = self.env['account.move.line']
        for lines in self.invoice_lines:
            line_to_reconcile += lines.move_line_id.filtered(lambda r: not r.reconciled and r.account_id.internal_type in ('payable', 'receivable'))
        return (line_to_reconcile + payment_line).reconcile(writeoff_acc_id, writeoff_journal_id)
    
    
#     def _get_shared_move_line_vals(self, debit, credit, amount_currency, move_id, invoice_id=False):
#         """ Returns values common to both move lines (except for debit, credit and amount_currency which are reversed)
#         """
#         return {
#             'partner_id': self.payment_type in ('inbound', 'outbound') and self.env['res.partner']._find_accounting_partner(self.partner_id).id or False,
#             'invoice_id': invoice_id and invoice_id.id or False,
#             'move_id': move_id,
#             'debit': debit,
#             'credit': credit,
#             'amount_currency': amount_currency or False,
#         }
    def _get_tax_move_line_vals(self, invoice=False):
        if self.payment_type == 'transfer':
            name = self.name
        else:
            name = ''
            if self.partner_type == 'customer':
                if self.payment_type == 'inbound':
                    name += _("Customer Payment")
                elif self.payment_type == 'outbound':
                    name += _("Customer Refund")
            elif self.partner_type == 'supplier':
                if self.payment_type == 'inbound':
                    name += _("Vendor Refund")
                elif self.payment_type == 'outbound':
                    name += _("Vendor Payment")
            if invoice:
                name += ': '
                for inv in invoice:
                    if inv.move_id:
                        name += inv.number + ', '
                name = name[:len(name)-2] 
        return {
            'name': name,
            'account_id': self.tax_id.account_id.id,
            'journal_id': self.journal_id.id,
            'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
            'payment_id': self.id,
        }
        
    #  <-- START Code added by Srikesh Infotech for convert check amount to word
    @api.depends('check_amount')
    def get_check_amount_in_word(self):
        amount_word = self.currency_id.amount_to_text(self.check_amount)
        self.check_amount_in_word =amount_word
    # ENDED convert check amount to word -->
    
    # <-- START Code added by Srikesh Infotech for calculate check amount value
    # (Payment Amount - Withholding Tax Amount)
    @api.depends('amount','tax_amount')
    def get_check_amount(self):
        amount = self.amount
        tax_amount = self.tax_amount        
        check_amount =(amount - float(tax_amount))
        self.check_amount = check_amount
    # ENDED calculate check amount value -->
        
class AccountTax(models.Model):
    _inherit = 'account.tax'
    
    is_withholding_tax = fields.Boolean('Is withholding', default=False)
    
    
class AccountMove(models.Model):
    _inherit = 'account.move.line'
    
    is_select = fields.Boolean('Select', default=False)
    