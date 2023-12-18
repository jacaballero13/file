from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountMoveCharges(models.Model):
    _inherit = 'account.move'

    # elmo: Added new field for charges
    net_charges = fields.Monetary(string="Net Charges",
                                readonly=True,  domain=[('type', '=', 'out_invoice')])
    vat_charges = fields.Monetary(string='VAT Charges',  domain=[('type', '=', 'out_invoice')])

    def get_vatcharges_accounts(self):
        params = self.env['ir.config_parameter'].sudo()
        vat_id = int(params.get_param('vat', default=0))
        vat = self.env['account.tax'].search([('id', '=', vat_id)])
        account_id = 0
        for repartition in vat.invoice_repartition_line_ids:
            account_id = repartition.account_id.id

        return account_id

    def prepare_vatcharge_entry(self, param):

        res = ({
            'account_id': self.get_vatcharges_accounts(),
            'name': 'VAT Charges',
            'quantity': 1,
            'discount': 0,
            'credit': param.vat_charges,
            'balance': param.vat_charges * -1,
            'price_unit': param.vat_charges,
            'exclude_from_invoice_tab': True
        })

        return res

    def prepare_charge_entry(self, param):

        res = {
            'account_id': param.charge_id.account_charge_id,
            'name': "{}".format(param.charge_id.name),
            'quantity': 1,
            'discount': 0,
            'credit': param.charge_amount,
            'balance': param.charge_amount,
            'price_unit': param.charge_amount,
            'exclude_from_invoice_tab': True
        }
        return res

    @api.model_create_multi
    def create(self, vals_list):
        # OVERRIDE
        if any('state' in vals and vals.get('state') == 'posted' for vals in vals_list):
            raise UserError(_(
                'You cannot create a move already in the posted state. Please create a draft move and post it after.'))
        vat_charge_lines = []
        prepare_charge_lines = []
        for account_move in vals_list:
            if account_move.get('invoice_origin'):
                sales_order = self.env['sale.order'].search([('name', '=', account_move['invoice_origin'])])
                if account_move.get('type') in ['out_invoice'] and len(sales_order.charge_ids) > 0:
                    account_move['vat_charges'] = sales_order.vat_charges
                    # account_move['vat_activated'] = sales_order.vat_activated
                    account_move['invoice_line_ids'].append((0, 0, self.prepare_vatcharge_entry(sales_order)))
                else:
                    vat_charge_lines.append((0, 0, self.prepare_vatcharge_entry(sales_order))) 
                for charges in sales_order.charge_ids:
                    if account_move.get('type') in ['out_invoice']:
                        account_move['net_charges'] =sales_order.net_charges
                        account_move['total_charges'] = sales_order.total_charges
                        account_move['invoice_line_ids'].append((0, 0, self.prepare_charge_entry(charges)))
                    else:
                        prepare_charge_lines.append((0, 0, self.prepare_charge_entry(charges)))
        return super(AccountMoveCharges, self).create(vals_list)
