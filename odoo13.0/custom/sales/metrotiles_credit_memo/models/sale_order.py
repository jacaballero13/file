from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    credit_memo_ids = fields.Many2one(
        comodel_name='credit.memo.detail',
        string='Credit Memo',
    )
    credit_memo_count = fields.Integer(string='CM Forms', compute='get_cm_count')

    def get_cm_count(self):
        count = self.env['account.move'].search_count([('sale_order', '=', self.id), ('type','=','out_refund')])
        self.credit_memo_count = count

    # Redirect to Credit Memo Forms
    def open_credit_memo_lines(self):
        return {
            'name': _('Credit Memo Form'),
            'domain': [('sale_order', '=', self.id)],
            'view_type': 'form',
            'res_model': 'account.move',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }

    def get_credit_memo_request(self):
        view_id = self.env.ref('metrotiles_credit_memo.create_credit_memo_wizard_view')
        if view_id:
            req_wiz_data = {
                'name': "Credit Memo Request",
                'view_id': view_id.id,
                'view_mode': 'form',
                'view_type': 'form',
                'res_model': 'credit.memo.details',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'context': {
                    'sale_order_id': self.id,
                    'quotation_type': self.quotation_type,
                    'warehouse_id': self.warehouse_id.id,
                    'partner_id': self.partner_id.id,
                    'sales_ac': self.sales_ac.id,
                    }
            }
        return req_wiz_data
