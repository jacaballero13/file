from odoo import models, fields, api, exceptions
import json


class SaleOrderLinePrevVersion(models.Model):
    _name = 'metrotiles.sale.order.line.prev.version'
    _inherits = {'sale.order.line': 'sale_order_line_id'}

    def name_get(self):
        record = []

        for field in self:
            record.append((field.id, field.sale_order_line_id.id))

        return record