# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class MetrotilesAmendmentSaleOrderReasonWizard(models.TransientModel):
    _name = "metrotiles.amendment.sale.order.reason.wizard"
    _description = "Sale order reason wizard"

    reason = fields.Text(string='Reason', required=True)
    sale_order_ids = fields.Many2many('sale.order')

    is_reason_for = fields.Selection(
        [
            ('cancel_contract', 'Cancel Contract'),
            ('decline', 'Decline'),
        ],
        store=False,
        default=lambda self: self.env.context.get('is_reason_for')
    )

    @api.model
    def default_get(self, fields):
        res = super(MetrotilesAmendmentSaleOrderReasonWizard, self).default_get(fields)
        active_ids = self.env.context.get('active_ids', [])
        res.update({
            'sale_order_ids': active_ids,
        })

        return res

    def submit_decline_reason(self):
        self.sale_order_ids.action_sale_adjustment_refuse(self.reason)

    def cancel_contract_reason(self):
        self.sale_order_ids.action_sale_adjustment_cancel_contract_request(self.reason)