from datetime import datetime, timedelta
from functools import partial
from itertools import groupby

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import formatLang, get_lang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare



class TermsPopup(models.TransientModel):
    _name = 'metrotiles_procurement.terms_popup'
    _description = "Terms Popup"

    proforma_invoice_id = fields.Many2one(comodel_name="metrotiles_procurement.accounting_proforma_invoice",
                                                     readonly=True, required=True)
    due_date = fields.Datetime(default=datetime.today(),required=True)

    notes = fields.Text(required=True, default='')

    def action_confirm(self):
        terms = self.env['metrotiles_procurement.proforma_terms'].create({
            'proforma_invoice_id': self.proforma_invoice_id.id,
            'due_date': self.due_date,
            'notes': self.notes

        })
        self.proforma_invoice_id.update({
            'proforma_terms_id': terms.id
        })