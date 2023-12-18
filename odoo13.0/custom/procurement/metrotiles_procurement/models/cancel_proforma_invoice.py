from datetime import datetime, timedelta
from functools import partial
from itertools import groupby

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import formatLang, get_lang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare


class CancelProformaInvoice(models.TransientModel):
    _name = 'metrotiles_procurement.cancel_proforma_invoice'
    _description = "Proforma Invoice"

    accounting_proforma_invoice_id = fields.Many2one(comodel_name="metrotiles_procurement.accounting_proforma_invoice",
                                                     readonly=True, required=True)

    def action_confirm(self):
        approve_records = self.env['metrotiles_procurement.approved_proforma_invoice'].search([
            ('accounting_proforma_invoice_id', '=', self.accounting_proforma_invoice_id.id)
        ])
        if len(approve_records):
            approve_records[0].update({
                'status': 'cancelled',
                'remaining_amount': approve_records[0].grand_total
            })
        self.accounting_proforma_invoice_id.update({
            'state':'cancelled'
        })