from datetime import datetime, timedelta
from functools import partial
from itertools import groupby

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import formatLang, get_lang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare


class ApprovedProformaInvoice(models.Model):
    _name = 'metrotiles_procurement.approved_proforma_invoice'
    _description = "Proforma Invoice"

    accounting_proforma_invoice_id = fields.Many2one(comodel_name="metrotiles_procurement.accounting_proforma_invoice",
                                                     readonly=True, required=True)

    status = fields.Selection(selection=[
        ('cancelled', "Cancelled"),
        ('pending', "Pending"),
        ('approved', "Approved"),
    ], default='pending', required=True)

    currency_id = fields.Many2one(comodel_name='res.currency', related='accounting_proforma_invoice_id.currency_id')

    amount_total = fields.Monetary(string='Total Proforma Invoice Amount', related='accounting_proforma_invoice_id.amount_total')

    cancelled_payment = fields.Monetary(string="Payment from cancelled Proforma Invoice",
                                        compute='get_cancelled_proforma_invoice', store=True)

    # backloaded_payment

    total_credit_memo = fields.Monetary(string="Total Proforma Invoice Less Credit Memo", compute='get_total_credit_memo')

    discount = fields.Float(readonly=True)

    adjustment = fields.Monetary(readonly=True)

    grand_total = fields.Monetary(compute='get_grand_total')

    remaining_amount = fields.Monetary(readonly=True)


    @api.depends('accounting_proforma_invoice_id')
    def get_cancelled_proforma_invoice(self):
        cancelled_records = self.env['metrotiles_procurement.accounting_proforma_invoice'].search([
            ('partner_id', '=', self.accounting_proforma_invoice_id.partner_id.id)
        ])
        if len(cancelled_records):
            amount = 0
            for cancelled in cancelled_records:
                approve_proforma_records = self.env['metrotiles_procurement.approved_proforma_invoice'].search([
                    ('accounting_proforma_invoice_id', '=', cancelled.id)
                ], limit=1)
                if len(approve_proforma_records):
                    amount = amount + approve_proforma_records[0].remaining_amount
            self.cancelled_payment = amount

    @api.depends('cancelled_payment')
    def get_total_credit_memo(self):
        self.total_credit_memo = self.amount_total - self.cancelled_payment

    @api.depends('total_credit_memo','adjustment', 'discount')
    def get_grand_total(self):
        self.grand_total = round(self.total_credit_memo + self.adjustment - (self.amount_total * (self.discount/100)))

    def action_confirm(self):
        self.accounting_proforma_invoice_id.update({
            'state':'approved',

        })


