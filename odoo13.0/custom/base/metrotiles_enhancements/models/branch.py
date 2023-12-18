from odoo import models, fields, api

class BranchInherit(models.Model):
    _inherit = 'res.branch'

    branch_logo = fields.Binary(string="Logo")
    