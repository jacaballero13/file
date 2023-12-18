from datetime import datetime, timedelta
from functools import partial
from itertools import groupby

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import formatLang, get_lang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare


class PaymentDetailsPopup(models.TransientModel):
    _name = 'metrotiles_procurement.payment_details_popup'
    _description = "Payment Details Popup"

    proforma_invoice_id = fields.Many2one(comodel_name="metrotiles_procurement.accounting_proforma_invoice",
                                                     readonly=True, required=True)
    currency_id = fields.Many2one(string="Proforma Invoice Currency", comodel_name='res.currency', related='proforma_invoice_id.currency_id')

    amount_total = fields.Monetary(string='Proforma Invoice Amount', related='proforma_invoice_id.amount_total')

    adjustment = fields.Monetary(required=True, default=0)

    discount = fields.Float(default=0.0)

    payment_amount = fields.Monetary(required=True, default=0)

    # balance =

    grant_total = fields.Monetary(compute='get_grand_total')

    @api.depends('adjustment', 'discount')
    def get_grand_total(self):
        self.grant_total = round( self.amount_total + self.adjustment - (self.amount_total * (self.discount/100)))

    def action_confirm(self):
        self.env['metrotiles_procurement.approved_proforma_invoice'].create({
            'accounting_proforma_invoice_id': self.proforma_invoice_id.id,
            'adjustment': self.adjustment,
            'discount': self.discount
        })
        self.proforma_invoice_id.update({
            'state':'processing'
        })