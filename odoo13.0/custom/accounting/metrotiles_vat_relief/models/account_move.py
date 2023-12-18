# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError

class AccountMove(models.Model):
    ######################
    # Private attributes #
    ######################
    _inherit = 'account.move'

    is_activate_vat_releif = fields.Boolean(
        string='VAT Relief',
        default=True,
        store=True,
    )
    posting_date = fields.Date(
        string = "Posting Date",
        default=fields.Date.today(),
    )
    exempt = fields.Float(
        string="Exempt", 
        default=0.00,
    )
    zeroRated = fields.Float(
        string="ZeroRated",
        default=0.00,

    )
    is_exempt = fields.Boolean(
        string="Activate Exempt or ZeroRated ?"
    )
    
    slsales_id = fields.Many2one('metrotiles.bir_sls', string="SLS")
    slpurcahse_id = fields.Many2one('metrotiles.bir_slp', string="SLP")
    
    def button_draft(self):
        for rec in self:
            if rec.state in 'open':
                slp_obj = self.env['metrotiles.bir_slp'].search([('mt_move_id','=', self.slpurcahse_id.mt_move_id.id)])
                print(slp_obj)
                for each in slp_obj:
                    if slp_obj:
                        each.unlink()
                ss_obj = self.env['metrotiles.bir_slp'].search([('mt_move_id', '=', self.slsales_id.mt_move_id.id)])
                for each in ss_obj:
                    if ss_obj:
                        each.unlink()
        return super(AccountMove, self).button_draft()
    
    ##################
    # Action methods #
    ##################

    def action_post(self): 
        taxable_net_vat = 0.00
        input_vat = self.amount_vat
        total_purchases = self.amount_total
        exempt = self.exempt if self.is_exempt and self.exempt > 0 else None 
        zeroRated = self.zeroRated if self.is_exempt and self.exempt > 0 else None 
        goods = 0
        capital = 0
        service = 0
        gross_tot = self.amount_discounted_total 
        for invoice in self.invoice_line_ids:
            product_id = invoice.product_id.id
            product = self.env['product.product'].search([('id','=', product_id )])
            for lines in invoice:
                if lines.tax_ids:
                    taxable_net_vat += lines.price_subtotal
            for products in product:
                if products.type in ['consu', 'product'] :
                    goods += invoice.price_subtotal
                elif products.type == "capital":
                    capital += invoice.price_subtotal
                elif product.type == 'service':
                        service += invoice.price_subtotal
                else:
                    raise UserError('No Product type set')
        if self.is_activate_vat_releif:
            move_slp_obj = self.env['metrotiles.bir_slp']
            if not move_slp_obj and self.type == 'in_invoice':
                slp_obj = move_slp_obj.create({ 
                    'mt_move_id': self.id,
                    'mt_branch': self.branch_id.id,
                    'mt_date': self.posting_date,
                    'mt_ref': self.ref,
                    'mt_tin': self.partner_id.vat,
                    'mt_partner_id': self.partner_id.id,
                    'mt_address': self.partner_id.invoice_address,
                    'mt_net_vat': taxable_net_vat,
                    'mt_services': service,
                    'mt_capital': capital,
                    'mt_goods': goods,
                    'mt_input': input_vat,
                    'mt_gross_amount': gross_tot,
                    'mt_account_id': invoice.account_id.id,
                })
                move_slp_obj = slp_obj.id
                self.update({'slpurcahse_id': move_slp_obj})
            move_sls_obj = self.env['metrotiles.bir_sls']
            if not move_sls_obj and self.type == 'out_invoice':
                sls_obj = move_sls_obj.create({
                    'mt_move_id': self.id,
                    'mt_branch': self.branch_id.id,
                    'mt_date': self.posting_date,
                    'mt_ref': self.ref,
                    'mt_tin': self.partner_id.vat,
                    'mt_partner_id': self.partner_id.id,
                    'mt_address': self.partner_id.invoice_address,
                    'mt_services': service,
                    'mt_goods': goods,
                    'mt_zero_rated': zeroRated,
                    'mt_output_tax': input_vat,
                    'mt_gross_sales': gross_tot,
                    'mt_account_id': invoice.account_id.id,
                    }
                )
                move_sls_obj = sls_obj.id
                self.update({'slsales_id': move_sls_obj})
        return super(AccountMove, self).action_post()
