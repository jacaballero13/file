from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def run_sql(self, qry):
        self._cr.execute(qry)
        _res = self._cr.fetchall()
        return _res

    # def get_product_list_rfq_po_template(self):
    #     contract_id
    #     for rec in


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    client_name = fields.Char(related='indention_id.customer', store=True)
    x_prod_id = fields.Char(related='product_id.default_code', store=True)
    x_contract_name = fields.Char(related='indention_id.name', store=True)
