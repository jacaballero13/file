from datetime import datetime, timedelta
from functools import partial
from itertools import groupby

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import formatLang, get_lang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare



class ProformaTerms(models.Model):
    _name = 'metrotiles_procurement.proforma_terms'
    _description = "Terms Popup"

    proforma_invoice_id = fields.Many2one(comodel_name="metrotiles_procurement.accounting_proforma_invoice",
                                                     readonly=True, required=True)
    due_date = fields.Datetime(default=datetime.today(),required=True)

    notes = fields.Text(required=True)

    @api.model
    def create(self, vals_list):
        return super(ProformaTerms, self).create(vals_list);