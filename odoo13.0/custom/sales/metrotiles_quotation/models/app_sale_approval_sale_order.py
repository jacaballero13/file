from odoo import models
from odoo.tools import float_compare


class AppSaleApprovalSaleOrder(models.Model):
    _inherit = 'sale.order'

    def _compute_workflow(self):
        for rec in self:
            currency = rec.company_id.currency_id
            limit_amount = rec.company_id.so_double_approval_amount
            limit_amount = currency.compute(limit_amount, rec.currency_id)
            flag_so_double_approval = rec.company_id.so_double_approval == 'two_step'
            flag_so_double_check = rec.company_id.so_double_check == 'two_step'

            flag_amount_to_approve = float_compare(
                limit_amount, rec.amount_total,
                precision_rounding=rec.currency_id.rounding) <= 0
            rec.is_to_approve = (flag_so_double_approval and flag_amount_to_approve) or rec.need_approval
            rec.is_to_check = flag_so_double_check
