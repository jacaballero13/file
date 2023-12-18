from odoo import models, fields, api


class MetrotilesSaleIndention(models.Model):
    _inherit = 'metrotiles.sale.indention'

    date_order = fields.Datetime(related='sale_line_id.order_id.date_order', string="Order Date")