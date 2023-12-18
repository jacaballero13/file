from psycopg2 import OperationalError, Error

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
from odoo.tools.float_utils import float_compare, float_is_zero, float_round

import logging

_logger = logging.getLogger(__name__)

# class StockRule(models.Model):
#     def _prepare_mo_vals(self, product_id, product_qty, product_uom, location_id, name, origin, company_id, values, bom, warehouse=False):
#         # date_deadline = fields.Datetime.to_string(self._get_date_planned(product_id, company_id, values))
#         return {
#             'origin': origin,
#             'product_id': product_id.id,
#             'product_qty': product_qty,
#             'product_uom_id': product_uom.id,
#             'location_src_id': location_id,
#             'location_dest_id': location_id,
#             'origin': name,
#             'bom_id': bom.id,
#             'date_deadline': False,
#             'date_planned_finished': False,
#             'date_planned_start': False,
#             'procurement_group_id': False,
#             'propagate_cancel': False,
#             'propagate_date': False,
#             'propagate_date_minimum_delta': False,
#             'orderpoint_id': values.get('orderpoint_id', False) and values.get('orderpoint_id').id if not warehouse else False,
#             'picking_type_id': self.picking_type_id.id or values['warehouse_id'].manu_type_id.id if not warehouse else warehouse.manu_type_id.id,
#             'company_id': company_id.id,
#             'move_dest_ids': values.get('move_dest_ids') and [(4, x.id) for x in values['move_dest_ids']] or False,
#             'user_id': False,
#         }

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    temp_reserved = fields.Integer(string="Temporary Reserved", default=0)

    on_hand = fields.Integer(string="On Hand",
                             compute="get_on_hand_qty",
                             help="On hand Quantity deducted by temp. reserved and cont. reserved", store=True)

    variant = fields.Char(string="Variant", compute="get_variant_from_product")
    size = fields.Char(string="Sizes (cm)", compute="get_variant_from_product")

    reserved_quantity = fields.Integer(
        'Reserved Quantity',
        default=0.0,
        help='Quantity of reserved products in this quant, in the default unit of measure of the product',
        readonly=True, required=True)

    @api.depends('quantity', 'reserved_quantity', 'temp_reserved')
    def get_on_hand_qty(self):
        for rec in self:
            rec.update({'on_hand': rec.quantity - (rec.reserved_quantity + rec.temp_reserved)})

    @api.depends('product_id')
    def get_variant_from_product(self):
        for rec in self:
            variant = 'N/A'
            size = 'N/A'

            for attr in rec.product_id.product_template_attribute_value_ids:
                if attr.attribute_id.name == 'Variants':
                    variant = attr.name
                elif attr.attribute_id.name == 'Sizes':
                    size = attr.name

            rec.update({'variant': variant, 'size': size})

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
            available_quantity = (sum(quants.mapped('quantity')) - sum(quants.mapped('reserved_quantity'))) - sum(
                quants.mapped('temp_reserved'))
            if allow_negative:
                return available_quantity
            else:
                print(available_quantity if float_compare(available_quantity, 0.0,
                                                          precision_rounding=rounding) >= 0.0 else 0.0)
                return available_quantity if float_compare(available_quantity, 0.0,
                                                           precision_rounding=rounding) >= 0.0 else 0.0
        else:
            availaible_quantities = {lot_id: 0.0 for lot_id in list(set(quants.mapped('lot_id'))) + ['untracked']}
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
    def _unlink_zero_quants(self):
        """ _update_available_quantity may leave quants with no
        quantity and no reserved_quantity. It used to directly unlink
        these zero quants but this proved to hurt the performance as
        this method is often called in batch and each unlink invalidate
        the cache. We defer the calls to unlink in this method.
        """
        precision_digits = max(6, self.sudo().env.ref('product.decimal_product_uom').digits * 2)

        locations = []

        for warehouse in self.env['stock.warehouse'].get_warehouses():
            locations.append(warehouse.lot_stock_id.id)

        # Use a select instead of ORM search for UoM robustness.
        query = """SELECT id 
            FROM stock_quant 
            WHERE (round(quantity::numeric, %s) = 0 OR quantity IS NULL) 
                AND round(reserved_quantity::numeric, %s) = 0 AND location_id not in %s;"""
        params = (precision_digits, precision_digits, tuple(locations))
        self.env.cr.execute(query, params)
        quant_ids = self.env['stock.quant'].browse([quant['id'] for quant in self.env.cr.dictfetchall()])
        quant_ids.sudo().unlink()

    def get_prev_available(self, prev_qty):
        tem_reserved = 0

        if prev_qty > 0:
            tem_reserved = self.temp_reserved - prev_qty
        else:
            tem_reserved = self.temp_reserved

        return (self.quantity - self.reserved_quantity) - tem_reserved

    def get_available(self):
        return (self.quantity - self.reserved_quantity) - self.temp_reserved

    def update_temp_reserved(self, qty, isAdd=True):
        if isAdd:
            self.update({'temp_reserved': self.temp_reserved + qty})
        else:
            self.update({'temp_reserved': self.temp_reserved - qty})

    def get_by_location_and_product(self, stock_location, product, package):
        return self.search([('location_id', '=', stock_location.id), ('product_id', '=', product.id), ('package_id', '=', package)])

    def get_available_qty(self):
        return (self.quantity - self.reserved_quantity) - self.temp_reserved