from odoo import models, fields

class SaleOrderTemplate(models.Model):
    _inherit = "sale.order.template"

    need_approval = fields.Boolean(string="Need Approval", default=False)
