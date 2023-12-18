

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    stock_request_allow_virtual_loc = fields.Boolean(
        string="Allow Virtual locations on Stock Requests"
    )
