from datetime import datetime, timedelta
from functools import partial
from itertools import groupby

from odoo import api, fields, models, SUPERUSER_ID, _, exceptions
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import formatLang, get_lang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare

class ProformaInvoiceItems(models.Model):
    _inherit = 'metrotiles_procurement.proforma_invoice_item'



    shipment_id = fields.Many2one(comodel_name="shipment.number", string="Shipment No.",readonly=True, store=True)