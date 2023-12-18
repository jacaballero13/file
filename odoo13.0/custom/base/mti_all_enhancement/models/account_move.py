from locale import currency
import pstats
from odoo import models, fields, api
from odoo.tools.float_utils import float_compare
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    
    def _get_default_rate(self):
        return self.env['res.currency'].search([('name','=','PHP')]).rate

    currency_rate = fields.Float(default=_get_default_rate, store=True)

    def updateCurrencyRate(self):
        pass
        # currency_id = self.env['res.currency.rate'].search([('currency_id', '=', 36)])
        # currency_id.update({'rate': self.currency_rate})

    @api.onchange('currency_rate','currency_id')
    def _exchange_currency_rate(self):
        for rec in self:
            # currency_id = rec.env['res.currency.rate'].search([('currency_id', '=', 36)])
            # currency_id.update({'rate': rec.currency_rate})
            currency_id = rec.env['res.currency'].search([('name','=','PHP')])
            currency_rate_amount = rec.env['res.currency.rate'].search([('currency_id', '=', currency_id.id)])
            currency_rate_amount.update({'rate': rec.currency_rate})
            
        self.with_context(check_move_validity=False)._recompute_dynamic_lines(
            recompute_all_taxes=False, recompute_tax_base_amount=True)

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    price_type = fields.Selection(selection=[('per_piece',"PC"),('per_sqm',"SQM")])
    qty_sqm = fields.Float()

    
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
        subtotal = 0
        # Compute 'price_subtotal'.
            
        price_unit_wo_discount = price_unit * (1 - (discount / 100.0))
        subtotal = quantity * price_unit_wo_discount
        
        if self.move_id.type=='in_invoice':
            if self.price_type=='per_sqm':
                subtotal = self.qty_sqm * self.price_net

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
        
class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    
    def _prepare_account_move_line(self, move):
        self.ensure_one()
        if self.product_id.purchase_method == 'purchase':
            qty = self.product_qty - self.qty_invoiced
        else:
            qty = self.qty_received - self.qty_invoiced
        if float_compare(qty, 0.0, precision_rounding=self.product_uom.rounding) <= 0:
            qty = 0.0

        if self.currency_id == move.company_id.currency_id:
            currency = False
        else:
            currency = move.currency_id

        return {
            'name': '%s: %s' % (self.order_id.name, self.name),
            'move_id': move.id,
            'currency_id': currency and currency.id or False,
            'purchase_line_id': self.id,
            'date_maturity': move.invoice_date_due,
            'product_uom_id': self.product_uom.id,
            'product_id': self.product_id.id,
            'price_unit': self.price_unit,
            'price_type': self.price_type,
            'qty_sqm': self.qty_sqm,
            'quantity': qty,
            'partner_id': move.partner_id.id,
            'analytic_account_id': self.account_analytic_id.id,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
            'tax_ids': [(6, 0, self.taxes_id.ids)],
            'display_type': self.display_type,
        }
        
    