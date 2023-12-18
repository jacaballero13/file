# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime


class AccountMove(models.Model):
    _inherit = 'account.move'
    
    branch_id = fields.Many2one(comodel_name='res.branch',required=True)
    is_vatable = fields.Selection(selection=[('vat','Vatable'),
                                            ('non_vat', 'Non Vatable')],default='non_vat',string='VAT')

    @api.model
    def create(self, vals):
        res = super(AccountMove,self).create(vals)
        branch_id = vals.get('branch_id', None)
        current_date=datetime.now()

        if branch_id:
            branch_prefix = self.env['res.branch'].search([('id','=',branch_id)])
            sequence = self.env['ir.sequence'].search([('id','=',res.journal_id.sequence_id.id)])
            if res.type == 'out_invoice':
                if branch_prefix:
                    sequence.update({'prefix': '%s/%s/%s/' % ("CUST", branch_prefix.branch_sequence, current_date.year)})
                    
                if not branch_prefix:
                    raise UserError('Branch sequence must be set.')
                    

            if res.type == 'in_invoice':
                if branch_prefix:
                    sequence.update({'prefix': '%s/%s/%s/' % ("APV", branch_prefix.branch_sequence,current_date.year)})
                    
                if not branch_prefix:
                    raise UserError('Branch sequence must be set.')
                
        if res.amount_vat or res.is_vatable or res.vatable:
            res.is_vatable = 'vat'
        return res

    # Change customer invoices sequence if branch is updated
    def post(self):
        to_write = {'state': 'posted'}
        for move in self:
            if len(move.name) > 0:
                # Get the journal's sequence.
                sequence = move._get_sequence()
                if not sequence:
                    raise UserError(_('Please define a sequence on your journal.'))

                to_write['name'] = sequence.next_by_id(sequence_date=move.date)
                move.write(to_write)
        return super(AccountMove, self).post()
    
    # Write sequence per branch if user made changes
    def write(self, vals):
        res = super(AccountMove,self).write(vals)
        branch_id = self.branch_id.id
        current_date=datetime.now()

        for rec in self:
            if rec.state == 'draft':
                if branch_id:
                    branch_prefix = self.env['res.branch'].search([('id','=',branch_id)])
                    sequence = self.env['ir.sequence'].search([('id','=',self.journal_id.sequence_id.id)])
                    if rec.type == 'out_invoice':
                        if branch_prefix:
                            # raise UserError(sequence.name)
                            
                            sequence.update({'prefix': '%s/%s/%s/' % ("CUST", branch_prefix.branch_sequence, current_date.year)})
                    
                        if not branch_prefix:
                            raise UserError('Branch sequence must be set.')
                            
                    if rec.type == 'in_invoice':
                        if branch_prefix:
                            sequence.update({'prefix': '%s/%s/%s/' % ("APV", branch_prefix.branch_sequence,current_date.year)})
                            
                        if not branch_prefix:
                            raise UserError('Branch sequence must be set.')
            # if rec.amount_vat or rec.is_vatable or rec.vatable:
            #     rec.is_vatable = 'vat'      
        return res

    