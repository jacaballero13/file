from odoo import models, fields, api, exceptions, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    def prepare_installtion_entries(self, data):
        total = data.net_price * data.uom_qty

        params = self.env['ir.config_parameter'].sudo()
        installation_account_id = int(params.get_param('installation_account', default=0))

        account = self.env['account.account'].search([('id', '=', installation_account_id)])

        return {
            'account_id': account.id,
            'product_id': data.product_id,
            'name': data.product_id.name,
            'quantity': data.uom_qty,
            'discount': 0,
            'credit': total,
            'price_net': data.net_price,
            'price_gross': data.gross_price,
            'price_unit': data.net_price,
        }
    def _reverse_moves(self, default_values_list=None, cancel=False):
        ''' Reverse a recordset of account.move.
        If cancel parameter is true, the reconcilable or liquidity lines
        of each original move will be reconciled with its reverse's.

        :param default_values_list: A list of default values to consider per move.
                                    ('type' & 'reversed_entry_id' are computed in the method).
        :return:                    An account.move recordset, reverse of the current self.
        '''
        # for rec in self:
        #     if len(rec.line_ids) > 0:
        #         raise UserError('Mohon maaf tidak bisa ..')
        
        return super(AccountMove, self)._reverse_moves()
        
    @api.model_create_multi
    def create(self, vals_list):
        # OVERRIDE
        if any('state' in vals and vals.get('state') == 'posted' for vals in vals_list):
            raise UserError(_(
                'You cannot create a move already in the posted state. Please create a draft move and post it after.'))

        for account_move in vals_list:
            if account_move.get('invoice_origin'):
                sales_order = self.env['sale.order'].search([('name', '=', account_move['invoice_origin'])])
                if len(sales_order.installation_ids) > 0:
                    account_move['invoice_line_ids'].append((0, 0, {
                        'display_type': 'line_section',
                        'name': 'Installation(s)',
                        'quantity': 0,
                        'discount': 0,
                        'credit': 0,
                        'price_unit': 0,
                        'account_id': None,
                    }))
                for installation in sales_order.installation_ids:
                    account_move['invoice_line_ids'].append((0, 0, self.prepare_installtion_entries(installation)))

        return super(AccountMove, self).create(vals_list)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    location_id = fields.Many2one('metrotiles.location', string="Location", store=True)
    application_id = fields.Many2one('metrotiles.application', string="Application", store=True)
    price_unit = fields.Float('Net Price', required=True, digits='Product Price', default=0.0)
    price_net = fields.Float(compute='_get_net_price', inverse_name="", string="Net Price")
    price_gross = fields.Monetary(string="Gross Price")

    factory_id = fields.Many2one('res.partner', string='Factory', store=True)
    series_id = fields.Many2one('metrotiles.series', string='Series', readonly=False, store=True)

    @api.depends('product_id', 'price_net')
    def _get_net_price(self):
        total_net = 0.0
        for line in self:
            total_net = line.price_unit * (1 - line.discount / 100)

            line.update({
                'price_net': total_net,
            })

    @api.model
    def _get_price_total_and_subtotal_model(self, price_unit, quantity, discount, currency, product, partner, taxes,
                                            move_type):
        ''' This method is used to compute 'price_total' & 'price_subtotal'.

        :param price_unit:  The current price unit.
        :param quantity:    The current quantity.
        :param discount:    The current discount.
        :param currency:    The line's currency.
        :param product:     The line's product.
        :param partner:     The line's partner.
        :param taxes:       The applied taxes.
        :param move_type:   The type of the move.
        :return:            A dictionary containing 'price_subtotal' & 'price_total'.
        '''
        res = {}

        # Compute 'price_subtotal'.
        price_unit_wo_discount = price_unit * (1 - (discount / 100.0))
        subtotal = quantity * price_unit_wo_discount

        # Compute 'price_total'.
        if taxes:
            taxes_res = taxes._origin.compute_all(price_unit_wo_discount,
                                                  quantity=quantity, currency=currency, product=product,
                                                  partner=partner, is_refund=move_type in ('out_refund', 'in_refund'))
            res['price_subtotal'] = taxes_res['total_excluded']
            res['price_total'] = taxes_res['total_included']
        else:
            res['price_total'] = res['price_subtotal'] = subtotal
        # In case of multi currency, round before it's use for computing debit credit
        if currency:
            res = {k: currency.round(v) for k, v in res.items()}
        return res
