from datetime import datetime, timedelta
from functools import partial
from itertools import groupby

from odoo import api, fields, models, SUPERUSER_ID, _, exceptions
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import formatLang, get_lang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare

# This module is for proforma invoice in procurement module

class ProformaInvoice(models.Model):
    _name = 'metrotiles_procurement.accounting_proforma_invoice'
    _description = "Accounting Proforma Invoice"
    _rec_name = 'purchase_proforma_invoice_id'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    purchase_proforma_invoice_id = fields.Many2one(comodel_name='metrotiles_procurement.proforma_invoice',
                                                   string="Proforma Invoice No.", required=True, tracking=True)
    purchase_order_id = fields.Many2one(comodel_name='purchase.order', related='purchase_proforma_invoice_id.purchase_order_id', tracking=True)

    # attachment = fields.Binary(string="Proforma Invoice Attachment")

    date_received = fields.Datetime(default=datetime.today(), tracking=True)

    currency_id = fields.Many2one(comodel_name='res.currency', related='purchase_proforma_invoice_id.currency_id', tracking=True)

    amount_total = fields.Monetary(string='Total', related='purchase_proforma_invoice_id.amount_total', tracking=True)

    partner_id = fields.Many2one(string="Vendor", comodel_name='res.partner', related='purchase_order_id.partner_id', tracking=True)

    status = fields.Selection(selection=[
        ('unpaid', "Unpaid"),
        ('paid', "Paid")
    ], default='unpaid', required=True, tracking=True)

    state = fields.Selection(selection=[
        ('cancelled', "Cancelled"),
        ('pending', "Pending"),
        ('processing', "Processing"),
        ('approved', "Approved"),
    ], default='pending', required=True, tracking=True)

    proforma_terms_id = fields.Many2one(comodel_name='metrotiles_procurement.proforma_terms')

    due_date = fields.Datetime(related='proforma_terms_id.due_date')

    notes = fields.Text(related='proforma_terms_id.notes')

    check_terms = fields.Boolean(compute='get_check_terms',default=False)

    def get_check_terms(self):
        self.check_terms = False
        for proforma in self:
            if len(proforma.proforma_terms_id) and proforma.state in ['cancelled', 'approved', 'processing']:
                proforma.check_terms = True

    def action_cancelled(self):
        view = self.env.ref('metrotiles_procurement.cancel_proforma_invoice_form')
        cancel_proforma_invoice = self.env['metrotiles_procurement.cancel_proforma_invoice'].create({
            'accounting_proforma_invoice_id': self.id
        })
        return {
            'name':"Cancel Confirmation",
            'view_mode': 'form',
            'view_id': view.id,
            'res_id': cancel_proforma_invoice.id,
            'view_type': 'form',
            'res_model': 'metrotiles_procurement.cancel_proforma_invoice',
            'type': 'ir.actions.act_window',
            'target': 'new',

        }

    def action_approved(self):
        view = self.env.ref('metrotiles_procurement.approved_proforma_invoice_form')
        approved_proforma_invoice = self.env['metrotiles_procurement.approved_proforma_invoice'].search([
            ('accounting_proforma_invoice_id', '=', self.id)
        ])
        return {
            'name': "Approve Payment Details",
            'view_mode': 'form',
            'view_id': view.id,
            'res_id': approved_proforma_invoice.id,
            'view_type': 'form',
            'res_model': 'metrotiles_procurement.approved_proforma_invoice',
            'type': 'ir.actions.act_window',
            'target': 'new',

        }

    def action_enter_payment_details(self):
        view = self.env.ref('metrotiles_procurement.payment_details_popup_form')
        payment_details_popup = self.env['metrotiles_procurement.payment_details_popup'].create({
            'proforma_invoice_id': self.id
        })
        return {
            'name': "Payment Details",
            'view_mode': 'form',
            'view_id': view.id,
            'res_id': payment_details_popup.id,
            'view_type': 'form',
            'res_model': 'metrotiles_procurement.payment_details_popup',
            'type': 'ir.actions.act_window',
            'target': 'new',

        }

    def action_terms(self):
        view = self.env.ref('metrotiles_procurement.terms_popup_form')
        terms_popup = self.env['metrotiles_procurement.terms_popup'].create({
            'proforma_invoice_id': self.id
        })
        return {
            'name': "Terms Popup",
            'view_mode': 'form',
            'view_id': view.id,
            'res_id': terms_popup.id,
            'view_type': 'form',
            'res_model': 'metrotiles_procurement.terms_popup',
            'type': 'ir.actions.act_window',
            'target': 'new',

        }