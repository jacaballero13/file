from psycopg2 import OperationalError, Error

from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError
from odoo.osv import expression
from odoo.tools.float_utils import float_compare, float_is_zero, float_round

import logging

_logger = logging.getLogger(__name__)


class StockQuantInherit(models.Model):
    _inherit = 'stock.quant'

    on_hand = fields.Boolean('On Hand', store=False, search='_search_on_hand')

    def get_by_location_and_product(self, stock_location, product, package=None):
        return self.search([('location_id', '=', stock_location.id), ('product_id', '=', product.id), ('package_id', '=', package)])

    def get_available_qty(self):
        return (self.quantity - self.reserved_quantity) - self.temp_reserved

    def update_temp_reserved(self, qty, isAdd=True):
        for rec in self:
            if isAdd:
                rec.update({'temp_reserved': rec.temp_reserved + qty})
            else:
                rec.update({'temp_reserved': rec.temp_reserved - qty})

    # Dats: Changed package to none
    def get_by_location_and_product(self, stock_location, product, package=None):
        return self.search([('location_id', '=', stock_location.id), ('product_id', '=', product.id), ])

    @api.model
    def _get_available_quantity(self, product_id, location_id, lot_id=None, package_id=None, owner_id=None,
                                strict=False, allow_negative=False):
        """ Return the available quantity, i.e. the sum of `quantity` minus the sum of
        `reserved_quantity`, for the set of quants sharing the combination of `product_id,
        location_id` if `strict` is set to False or sharing the *exact same characteristics*
        otherwise.
        This method is called in the following usecases:
            - when a stock move checks its availability
            - when a stock move actually assign
            - when editing a move line, to check if the new value is forced or not
            - when validating a move line with some forced values and have to potentially unlink an
              equivalent move line in another picking
        In the two first usecases, `strict` should be set to `False`, as we don't know what exact
        quants we'll reserve, and the characteristics are meaningless in this context.
        In the last ones, `strict` should be set to `True`, as we work on a specific set of
        characteristics.

        :return: available quantity as a float
        """
        self = self.sudo()
        quants = self._gather(product_id, location_id, lot_id=lot_id, package_id=package_id, owner_id=owner_id,
                              strict=strict)

        rounding = product_id.uom_id.rounding
        if product_id.tracking == 'none':
            available_quantity = (
                sum(quants.mapped('quantity')) - sum(quants.mapped('reserved_quantity')))

            if allow_negative:
                return available_quantity
            else:
                print(available_quantity if float_compare(available_quantity, 0.0,
                                                          precision_rounding=rounding) >= 0.0 else 0.0)
                return available_quantity if float_compare(available_quantity, 0.0,
                                                           precision_rounding=rounding) >= 0.0 else 0.0
        else:
            availaible_quantities = {lot_id: 0.0 for lot_id in list(
                set(quants.mapped('lot_id'))) + ['untracked']}
            for quant in quants:
                if not quant.lot_id:
                    availaible_quantities['untracked'] += (
                        quant.quantity - quant.reserved_quantity) - quant.temp_reserved
                else:
                    availaible_quantities[quant.lot_id] += (
                        quant.quantity - quant.reserved_quantity) - quant.temp_reserved
            if allow_negative:
                return sum(availaible_quantities.values())
            else:
                print(sum([available_quantity for available_quantity in availaible_quantities.values() if
                           float_compare(available_quantity, 0, precision_rounding=rounding) > 0]))
                return sum([available_quantity for available_quantity in availaible_quantities.values() if
                            float_compare(available_quantity, 0, precision_rounding=rounding) > 0])

    @api.model
    def _update_reserved_quantity(self, product_id, location_id, quantity, lot_id=None, package_id=None, owner_id=None, strict=False):
        """ Increase the reserved quantity, i.e. increase `reserved_quantity` for the set of quants
        sharing the combination of `product_id, location_id` if `strict` is set to False or sharing
        the *exact same characteristics* otherwise. Typically, this method is called when reserving
        a move or updating a reserved move line. When reserving a chained move, the strict flag
        should be enabled (to reserve exactly what was brought). When the move is MTS,it could take
        anything from the stock, so we disable the flag. When editing a move line, we naturally
        enable the flag, to reflect the reservation according to the edition.

        :return: a list of tuples (quant, quantity_reserved) showing on which quant the reservation
            was done and how much the system was able to reserve on it
        """
        self = self.sudo()
        rounding = product_id.uom_id.rounding
        quants = self._gather(product_id, location_id, lot_id=lot_id,
                              package_id=package_id, owner_id=owner_id, strict=strict)
        reserved_quants = []

        if float_compare(quantity, 0, precision_rounding=rounding) > 0:
            # if we want to reserve
            available_quantity = sum(quants.filtered(lambda q: float_compare(
                q.quantity, 0, precision_rounding=rounding) > 0).mapped('quantity')) - sum(quants.mapped('reserved_quantity'))
            if float_compare(quantity, available_quantity, precision_rounding=rounding) > 0:
                raise UserError(
                    _('It is not possible to reserve more products of %s than you have in stock.',)% product_id.display_name)
        elif float_compare(quantity, 0, precision_rounding=rounding) < 0:
            # if we want to unreserve
            available_quantity = sum(quants.mapped('reserved_quantity'))
            if float_compare(abs(quantity), available_quantity, precision_rounding=rounding) > 0:
                action_fix_unreserve = self.env.ref(
                    'stock.stock_quant_stock_move_line_desynchronization', raise_if_not_found=False)
                if action_fix_unreserve and self.user_has_groups('base.group_system'):
                    raise RedirectWarning(
                        _("""It is not possible to unreserve more products of %s than you have in stock.
The correction could unreserve some operations with problematics products.""", product_id.display_name),
                        action_fix_unreserve.id,
                        _('Automated action to fix it'))
                # else:
                #     raise UserError(_('It is not possible to unreserve more products of %s than you have in stock.') %
                #                     self.user_has_groups('base.group_system'))
                #     # raise UserError(
                    #     _("""It is not possible to unreserve more products of %s than you have in stock. Contact an administrator.""", self.user_has_groups('base.group_system')))
        else:
            return reserved_quants

        for quant in quants:
            if float_compare(quantity, 0, precision_rounding=rounding) > 0:
                max_quantity_on_quant = quant.quantity - quant.reserved_quantity
                if float_compare(max_quantity_on_quant, 0, precision_rounding=rounding) <= 0:
                    continue
                max_quantity_on_quant = min(max_quantity_on_quant, quantity)
                quant.reserved_quantity += max_quantity_on_quant
                reserved_quants.append((quant, max_quantity_on_quant))
                quantity -= max_quantity_on_quant
                available_quantity -= max_quantity_on_quant
            else:
                max_quantity_on_quant = min(
                    quant.reserved_quantity, abs(quantity))
                quant.reserved_quantity -= max_quantity_on_quant
                reserved_quants.append((quant, -max_quantity_on_quant))
                quantity += max_quantity_on_quant
                available_quantity += max_quantity_on_quant

            if float_is_zero(quantity, precision_rounding=rounding) or float_is_zero(available_quantity, precision_rounding=rounding):
                break
        return reserved_quants
