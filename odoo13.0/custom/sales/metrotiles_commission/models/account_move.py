from odoo import models, fields, api, exceptions, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _get_commission_account(self):
        params = self.env['ir.config_parameter'].sudo()
        commission_account_id = int(params.get_param('commission_account', default=0))

        return self.env['account.account'].search([('id', '=', commission_account_id)])

    def _prepare_architect_entry(self, param):
        title = param.architect_id.title.shortcut + " " if param.architect_id.title.shortcut else ''
        percent = " {} %".format(param.architect_commission) if param.architect_com_type == 'percentage' else ''

        res = {
            'account_id': self._get_commission_account().id,
            'name': "{}{}{}".format(title, param.architect_id.name, percent),
            'quantity': 1,
            'discount': 0,
            'balance': param.architect_subtotal_price,
            'price_unit': param.architect_subtotal_price * -1,
            'exclude_from_invoice_tab': True
        }

        return res

    def _prepare_designer_entry(self, param):
        title = param.designer_id.title.shortcut + " " if param.designer_id.title.shortcut else ''
        percent = " {} %".format(param.designer_commission) if param.designer_com_type == 'percentage' else ''

        res = {
            'account_id': self._get_commission_account().id,
            'name': "{}{}{}".format(title, param.designer_id.name, percent),
            'quantity': 1,
            'discount': 0,
            'balance': param.designer_subtotal_price,
            'price_unit': param.designer_subtotal_price * -1,
            'exclude_from_invoice_tab': True
        }

        return res

    # @api.model_create_multi
    # def create(self, vals_list):
    #     # OVERRIDE
    #     if any('state' in vals and vals.get('state') == 'posted' for vals in vals_list):
    #         raise UserError(_(
    #             'You cannot create a move already in the posted state. Please create a draft move and post it after.'))
    #     architect_lines = []
    #     designer_lines  = []
    #     for account_move in vals_list:
    #         if account_move.get('invoice_origin'):
    #             sales_order = self.env['sale.order'].search([('name', '=', account_move['invoice_origin'])])
    #             for architect in sales_order.architect_ids:
    #                 if account_move.get('type') in ['out_invoice']:
    #                     account_move['invoice_line_ids'].append((0, 0, self._prepare_architect_entry(architect)))
    #                 else:
    #                     architect_lines.append((0, 0, self._prepare_architect_entry(architect)))
    #             for designer in sales_order.designer_ids:
    #                 if account_move.get('type') in ['out_invoice']:
    #                     account_move['invoice_line_ids'].append((0, 0, self._prepare_designer_entry(designer)))
    #                 else:
    #                     designer_lines.append((0, 0, self._prepare_designer_entry(designer)))
    #     return super(AccountMove, self).create(vals_list)
