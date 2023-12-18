from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from odoo.tools import float_is_zero, float_compare, safe_eval, date_utils, email_split, email_escape_char, email_re
from odoo.tools.misc import formatLang, format_date, get_lang

from datetime import date, timedelta
from itertools import groupby
from itertools import zip_longest
from hashlib import sha256
from json import dumps


class AccountMove(models.Model):
    _inherit = "account.move"
    _descriptions = "To Enable Multiple Discounts"

    discounts = fields.Many2many('metrotiles.discount',
                                 'metrotiles_discount_account_move_rel',
                                 string="Discounts")
    amount_discount = fields.Float(string="Amount Discount", default=0.0)
    amount_discounted_total = fields.Monetary(string="amount_discounted_total", default=0.0,
                                              compute="_amount_total_with_discount")
    vatable = fields.Monetary(string="Amount Vat", default=0.0, store=True)
    total_charges = fields.Monetary(string="Charges Total", readonly=True,  domain=[('type', '=', 'out_invoice')])
    
    line_ids = fields.One2many('account.move.line', 'move_id', string='Journal Items', copy=True, readonly=True,
                               states={'draft': [('readonly', False)]}, domain=[('display_type', '=', False)])

    @api.depends('vatable', 'amount_discount', 'amount_untaxed', 'total_charges')
    def _amount_total_with_discount(self):
        for field in self:
            field.amount_discounted_total = field.amount_untaxed - field.amount_discount + field.vatable + field.total_charges

    def _get_discount_account(self):
        params = self.env['ir.config_parameter'].sudo()
        discount_account_id = int(params.get_param('discount_account', default=0))

        return self.env['account.account'].search([('id', '=', discount_account_id)])

    def _discount_entry(self, param):
        account = self._get_discount_account()

        res = {
            'account_id': account.id,
            'name': 'Discount',
            'quantity': 1,
            'discount': 0,
            'balance': param.amount_discount,
            'price_unit': -param.amount_discount,
            'exclude_from_invoice_tab': True
        }

        print(res)

        return res

    @api.model_create_multi
    def create(self, vals_list):
        # OVERRIDE
        if any('state' in vals and vals.get('state') == 'posted' for vals in vals_list):
            raise UserError(_(
                'You cannot create a move already in the posted state. Please create a draft move and post it after.'))
        discount_line = []
        for account_move in vals_list:
            if account_move.get('invoice_origin'):
                sales_order = self.env['sale.order'].search([('name', '=', account_move['invoice_origin'])])
                discounts = [(6, 0, list(map(lambda s: s.id, sales_order.total_discounts)))]
                account_move['amount_discount'] = sales_order.amount_discount
                account_move['discounts'] = discounts
                account_move['vatable'] = sales_order.amount_tax
                for in_line in account_move.get('invoice_line_ids', []):
                    if len(sales_order.column_discounts) <= 0:
                        break;

                    order_line = in_line[2]

                    if order_line.get('product_id', False):
                        product = self.env['product.product'].sudo().search([('id', '=', order_line.get('product_id', 0))], limit=1)

                        if product.product_tmpl_id.type == 'product':
                            order_line['discounts'] = [(6, 0, list(map(lambda s: s.id, sales_order.column_discounts)))]
                if account_move.get('type') == 'out_invoice':
                    account_move['invoice_line_ids'].append((0, 0, self._discount_entry(sales_order)))
                else:
                    discount_line.append((0, 0, self._discount_entry(sales_order)))

        return super(AccountMove, self).create(vals_list)

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    discounts = fields.Many2many('metrotiles.discount',
                                'metrotiles_discount_account_move_line_rel',
                                string="Discounts")