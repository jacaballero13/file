from datetime import datetime, timedelta
from functools import partial
from itertools import groupby

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import formatLang, get_lang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare


class TotalAmountDiscount(models.Model):
    _inherit = "sale.order"

    def _get_commission_account(self):
        params = self.env['ir.config_parameter'].sudo()
        commission_account_id = int(params.get_param('commission_account', default=0))

        return self.env['account.account'].search([('id', '=', commission_account_id)])

    def _get_discount_account(self):
        params = self.env['ir.config_parameter'].sudo()
        discount_account_id = int(params.get_param('discount_account', default=0))

        return self.env['account.account'].search([('id', '=', discount_account_id)])

    def _prepare_architect_entry(self, param):
        title = param.architect_id.title.shortcut + " " if param.architect_id.title.shortcut else False

        res = {
            'account_id': self._get_commission_account(),
            'name': title + param.architect_id.name,
            'quantity': 1,
            'discount': 0,
            'price_unit': param.architect_subtotal_price * -1,
            'exclude_from_invoice_tab': True
        }

        return res

    def _prepare_designer_entry(self, param):
        title = param.designer_id.title.shortcut + " " if param.designer_id.title.shortcut else ''

        res = {
            'account_id': self._get_commission_account(),
            'name': title + param.designer_id.name,
            'quantity': 1,
            'discount': 0,
            'price_unit': param.designer_subtotal_price * -1,
            'exclude_from_invoice_tab': True
        }

        return res

    def _discount_entry(self, param):
        params = self.env['ir.config_parameter'].sudo()
        vat = self.env['account.tax'].sudo().search([('id', '=', int(params.get_param('vat', default=0)))])

        res = {
            'account_id': self._get_commission_account(),
            'name': 'Discount ' + str(vat.amount) + '%' if vat.amount else 'Discount',
            'quantity': 1,
            'discount': 0,
            'price_unit': param * -1,
            'exclude_from_invoice_tab': True
        }

        return res

    def _create_invoices(self, grouped=False, final=False):
        """
        Create the invoice associated to the SO.
        :param grouped: if True, invoices are grouped by SO id. If False, invoices are grouped by
                        (partner_invoice_id, currency)
        :param final: if True, refunds will be generated if necessary
        :returns: list of created invoices
        """
        if not self.env['account.move'].check_access_rights('create', False):
            try:
                self.check_access_rights('write')
                self.check_access_rule('write')
            except AccessError:
                return self.env['account.move']

        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')

        # 1) Create invoices.
        invoice_vals_list = []
        for order in self:
            pending_section = None

            # Invoice values.
            invoice_vals = order._prepare_invoice()

            # Invoice line values (keep only necessary sections).
            for line in order.order_line:
                if line.display_type == 'line_section':
                    pending_section = line
                    continue
                if float_is_zero(line.qty_to_invoice, precision_digits=precision):
                    continue
                if line.qty_to_invoice > 0 or (line.qty_to_invoice < 0 and final):
                    if pending_section:
                        invoice_vals['invoice_line_ids'].append((0, 0, pending_section._prepare_invoice_line()))
                        pending_section = None
                    invoice_vals['invoice_line_ids'].append((0, 0, line._prepare_invoice_line()))

            if not invoice_vals['invoice_line_ids']:
                raise UserError(_(
                    'There is no invoiceable line. If a product has a Delivered quantities invoicing policy, please make sure that a quantity has been delivered.'))

            invoice_vals_list.append(invoice_vals)

        # for field in self.architect_ids:

        if not invoice_vals_list:
            raise UserError(_(
                'There is no invoiceable line. If a product has a Delivered quantities invoicing policy, please make sure that a quantity has been delivered.'))

        # 2) Manage 'grouped' parameter: group by (partner_id, currency_id).
        if not grouped:
            new_invoice_vals_list = []
            invoice_grouping_keys = self._get_invoice_grouping_keys()
            for grouping_keys, invoices in groupby(invoice_vals_list,
                                                   key=lambda x: [x.get(grouping_key) for grouping_key in
                                                                  invoice_grouping_keys]):
                origins = set()
                payment_refs = set()
                refs = set()
                ref_invoice_vals = None
                for invoice_vals in invoices:
                    if not ref_invoice_vals:
                        ref_invoice_vals = invoice_vals
                    else:
                        ref_invoice_vals['invoice_line_ids'] += invoice_vals['invoice_line_ids']
                    origins.add(invoice_vals['invoice_origin'])
                    payment_refs.add(invoice_vals['invoice_payment_ref'])
                    refs.add(invoice_vals['ref'])
                ref_invoice_vals.update({
                    'ref': ', '.join(refs)[:2000],
                    'invoice_origin': ', '.join(origins),
                    'invoice_payment_ref': len(payment_refs) == 1 and payment_refs.pop() or False,
                })
                new_invoice_vals_list.append(ref_invoice_vals)
            invoice_vals_list = new_invoice_vals_list

        # added line of code
        for x in self:
            for field in x.architect_ids:
                invoice_vals_list[0]['invoice_line_ids'].append(self._prepare_architect_entry(field))

            for field in x.designer_ids:
                invoice_vals_list[0]['invoice_line_ids'].append(self._prepare_designer_entry(field))

            if x.amount_discount > 0:
                invoice_vals_list[0]['invoice_line_ids'].append(self._discount_entry(x.amount_discount))

        # 3) Create invoices.
        # Manage the creation of invoices in sudo because a salesperson must be able to generate an invoice from a
        # sale order without "billing" access rights. However, he should not be able to create an invoice from scratch.
        moves = self.env['account.move'].sudo().with_context(default_type='out_invoice').create(invoice_vals_list)
        # 4) Some moves might actually be refunds: convert them if the total amount is negative
        # We do this after the moves have been created since we need taxes, etc. to know if the total
        # is actually negative or not
        if final:
            moves.sudo().filtered(lambda m: m.amount_total < 0).action_switch_invoice_into_refund_credit_note()
        for move in moves:
            move.message_post_with_view('mail.message_origin_link',
                                        values={'self': move, 'origin': move.line_ids.mapped('sale_line_ids.order_id')},
                                        subtype_id=self.env.ref('mail.mt_note').id
                                        )

        return moves
