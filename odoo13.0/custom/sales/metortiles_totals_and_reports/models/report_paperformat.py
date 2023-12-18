from odoo import models, fields, api
from functools import partial
from odoo.tools.misc import formatLang, get_lang


class ReportPaperFormat(models.Model):
    _inherit = "report.paperformat"
    margin_top = fields.Float('Top Margin (mm)', default=7)
