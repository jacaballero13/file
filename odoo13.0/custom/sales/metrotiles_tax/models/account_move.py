from odoo import models, fields, api, exceptions, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'
    # amount_vat = fields.Monetary(string="Amount Tax", default=0.0)

    def _get_vat_accounts(self, base_tax):
        params = self.env['ir.config_parameter'].sudo()
        vat_id = int(params.get_param('vat', default=0))
        vat = self.env['account.tax'].search([('id', '=', vat_id)])
        tax_calculated = 0
        partitions = []
        for repartition in vat.invoice_repartition_line_ids:
            if repartition.repartition_type == 'tax' and tax_calculated < 100:
                percentage = base_tax * (repartition.factor_percent / 100)
                partitions.append({'account': repartition.account_id, 'percentage': percentage})
                tax_calculated += repartition.factor_percent

        return {'label': vat.name,'partitions': partitions}

    def prepare_vat_entry(self, base_tax):
        res = []
        partitioned_tax = self._get_vat_accounts(base_tax)

        for pt in partitioned_tax.get('partitions'):
            res.append( {
                'account_id': pt.get('account').id,
                'name': partitioned_tax.get('label'),
                'quantity': 1,
                'discount': 0,
                'credit': pt.get('percentage'),
                'balance': pt.get('percentage') * -1,
                'price_unit': pt.get('percentage'),
                'exclude_from_invoice_tab': True
            })

        return res

    @api.model_create_multi
    def create(self, vals_list):
        # OVERRIDE
        if any('state' in vals and vals.get('state') == 'posted' for vals in vals_list):
            raise UserError(_(
                'You cannot create a move already in the posted state. Please create a draft move and post it after.'))
        tax_line = []
        for account_move in vals_list:
            if account_move.get('invoice_origin'):
                sales_order = self.env['sale.order'].search([('name', '=', account_move['invoice_origin'])])

                for entry in self.prepare_vat_entry(sales_order.amount_tax):
                    if account_move.get('type') in ['out_invoice'] and len(entry) > 0:
                        account_move['invoice_line_ids'].append((0, 0, entry))
                    else:
                        tax_line.append((0, 0, entry))
        return super(AccountMove, self).create(vals_list)
