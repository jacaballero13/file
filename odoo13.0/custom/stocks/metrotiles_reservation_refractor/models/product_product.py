
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
from odoo.tools.float_utils import float_compare, float_is_zero, float_round


class ProductProduct(models.Model):
    _inherit = 'product.product'

    sales_reserved_qty = fields.Integer(
        string="Sales QTY on hand", compute="_get_remaining_stock_sale")
    # Dats: changed temporary reserve
    temporary_reserved_qty = fields.Float(
        'Temp. Reserved', compute='_get_temp_and_reserved',
        digits='Product Unit of Measure', compute_sudo=False,
        help="Reserved Product")

    reserved_qty = fields.Float(
        'Reserved', compute='_get_temp_and_reserved',
        digits='Product Unit of Measure', compute_sudo=False,
        help="Reserved Product")

    qty_available = fields.Integer(
        string="Qty Available")

    on_hand_qty = fields.Integer(string="On Hand")

    @api.depends('temporary_reserved_qty', 'reserved_qty')
    def _get_temp_and_reserved(self):
        for record in self:
            temp_reserve_product_id = self.env['metrotiles.product.temp.reserved'].search(
                [('product_id', '=', record.id)])
            cont_reserve_product_id = self.env['metrotiles.product.reserved'].search(
                [('product_id', '=', record.id)])
        total_reserve = 0
        total_temp_reserved = 0
        for rec in temp_reserve_product_id:
            total_temp_reserved += rec.quantity
        for reserve in cont_reserve_product_id:
            total_reserve += reserve.quantity

        self.reserved_qty = total_reserve
        self.temporary_reserved_qty = total_temp_reserved

    @api.depends('qty_available', 'temporary_reserved_qty', 'reserved_qty')
    def _get_remaining_stock_sale(self):
        reserved_qty = 0
        total_qty_onhand = 0
        on_hand = 0
        for rec in self:

            stock_quant = self.env['stock.quant'].search(
                [('product_id', '=', rec.id), ('location_id.usage', '=', 'internal'),('location_id.name','!=','Output'),
                ('location_id.name','!=','BREAKAGE'),('location_id.name','!=','Packing Zone')])

            for stocks in stock_quant:
                if stocks.quantity > 0:
                    total_qty_onhand += stocks.quantity
                    reserved_qty += stocks.reserved_quantity

            total = total_qty_onhand - \
                    reserved_qty - rec.temporary_reserved_qty
            
            rec.sales_reserved_qty = total
            on_hand = rec.sales_reserved_qty
        
        self.on_hand_qty = on_hand
    # Dats: Product View Remove Temp Reserve

    def _compute_quantities(self):
        products = self.filtered(lambda p: p.type != 'service')
        res = products._compute_quantities_dict(self._context.get('lot_id'), self._context.get(
            'owner_id'), self._context.get('package_id'), self._context.get('from_date'), self._context.get('to_date'))

        for product in products:
            product.qty_available = res[product.id]['qty_available']
            product.incoming_qty = res[product.id]['incoming_qty']
            product.outgoing_qty = res[product.id]['outgoing_qty']
            product.virtual_available = res[product.id]['virtual_available']
            product.free_qty = res[product.id]['free_qty']
            product.reserved_qty = res[product.id]['reserved_qty']

            # Dats removed:
            # product.temporary_reserved_qty = res[product.id]['temporary_reserved_qty']
            # Dats added
            #

        if len(products) <= 0:
            self.reserved_qty = 0
            self.temporary_reserved_qty = 0

        # Services need to be set with 0.0 for all quantities
        services = self - products
        services.qty_available = 0.0
        services.reserved_qty = 0.0
        services.temporary_reserved_qty = 0.0
        services.incoming_qty = 0.0
        services.outgoing_qty = 0.0
        services.virtual_available = 0.0
        services.free_qty = 0.0
        services.on_hand_qty = 0.0

    def _compute_quantities_dict(self, lot_id, owner_id, package_id, from_date=False, to_date=False):
        domain_quant_loc, domain_move_in_loc, domain_move_out_loc = self._get_domain_locations()
        domain_quant = [('product_id', 'in', self.ids)] + domain_quant_loc
        dates_in_the_past = False
        # only to_date as to_date will correspond to qty_available
        to_date = fields.Datetime.to_datetime(to_date)
        if to_date and to_date < fields.Datetime.now():
            dates_in_the_past = True

        domain_move_in = [('product_id', 'in', self.ids)] + domain_move_in_loc
        domain_move_out = [('product_id', 'in', self.ids)
                           ] + domain_move_out_loc
        if lot_id is not None:
            domain_quant += [('lot_id', '=', lot_id)]
        if owner_id is not None:
            domain_quant += [('owner_id', '=', owner_id)]
            domain_move_in += [('restrict_partner_id', '=', owner_id)]
            domain_move_out += [('restrict_partner_id', '=', owner_id)]
        if package_id is not None:
            domain_quant += [('package_id', '=', package_id)]
        if dates_in_the_past:
            domain_move_in_done = list(domain_move_in)
            domain_move_out_done = list(domain_move_out)
        if from_date:
            date_date_expected_domain_from = [
                '|',
                '&',
                ('state', '=', 'done'),
                ('date', '<=', from_date),
                '&',
                ('state', '!=', 'done'),
                ('date_expected', '<=', from_date),
            ]
            domain_move_in += date_date_expected_domain_from
            domain_move_out += date_date_expected_domain_from
        if to_date:
            date_date_expected_domain_to = [
                '|',
                '&',
                ('state', '=', 'done'),
                ('date', '<=', to_date),
                '&',
                ('state', '!=', 'done'),
                ('date_expected', '<=', to_date),
            ]
            domain_move_in += date_date_expected_domain_to
            domain_move_out += date_date_expected_domain_to

        Move = self.env['stock.move']
        Quant = self.env['stock.quant']
        domain_move_in_todo = [('state', 'in',
                                ('waiting', 'confirmed', 'assigned', 'partially_available'))] + domain_move_in
        domain_move_out_todo = [('state', 'in',
                                 ('waiting', 'confirmed', 'assigned', 'partially_available'))] + domain_move_out
        moves_in_res = dict((item['product_id'][0], item['product_qty']) for item in
                            Move.read_group(domain_move_in_todo, ['product_id', 'product_qty'], ['product_id'],
                                            orderby='id'))
        moves_out_res = dict((item['product_id'][0], item['product_qty']) for item in
                             Move.read_group(domain_move_out_todo, ['product_id', 'product_qty'], ['product_id'],
                                             orderby='id'))
        quants_res = dict((item['product_id'][0], (item['quantity'], item['reserved_quantity'], item['temp_reserved'])) for item in
                          Quant.read_group(domain_quant, ['product_id', 'quantity', 'reserved_quantity', 'temp_reserved'],
                                           ['product_id'], orderby='id'))
        if dates_in_the_past:
            # Calculate the moves that were done before now to calculate back in time (as most questions will be recent ones)
            domain_move_in_done = [
                ('state', '=', 'done'), ('date', '>', to_date)] + domain_move_in_done
            domain_move_out_done = [
                ('state', '=', 'done'), ('date', '>', to_date)] + domain_move_out_done
            moves_in_res_past = dict((item['product_id'][0], item['product_qty']) for item in
                                     Move.read_group(domain_move_in_done, ['product_id', 'product_qty'], ['product_id'],
                                                     orderby='id'))
            moves_out_res_past = dict((item['product_id'][0], item['product_qty']) for item in
                                      Move.read_group(domain_move_out_done, ['product_id', 'product_qty'],
                                                      ['product_id'], orderby='id'))

        res = dict()
        for product in self.with_context(prefetch_fields=False):
            product_id = product.id
            if not product_id:
                res[product_id] = dict.fromkeys(
                    ['qty_available', 'free_qty', 'incoming_qty',
                        'outgoing_qty', 'virtual_available'],
                    0.0,
                )
                continue
            rounding = product.uom_id.rounding
            res[product_id] = {}
            if dates_in_the_past:
                qty_available = quants_res.get(product_id, [0.0])[0] - moves_in_res_past.get(product_id,
                                                                                             0.0) + moves_out_res_past.get(
                    product_id, 0.0)
            else:
                qty_available = quants_res.get(product_id, [0.0])[0]

            reserved_quantity = quants_res.get(
                product_id, [False, 0.0, 0.0])[1]
            temporary_reserved_qty = quants_res.get(
                product_id, [False, 0.0, 0.0])[2] or 0

            res[product_id]['qty_available'] = float_round(
                qty_available, precision_rounding=rounding)
            res[product_id]['free_qty'] = float_round(
                qty_available, precision_rounding=rounding)
            res[product_id]['incoming_qty'] = float_round(moves_in_res.get(product_id, 0.0),
                                                          precision_rounding=rounding)
            res[product_id]['outgoing_qty'] = float_round(moves_out_res.get(product_id, 0.0),
                                                          precision_rounding=rounding)
            res[product_id]['virtual_available'] = float_round(
                (qty_available) +
                res[product_id]['incoming_qty'] -
                res[product_id]['outgoing_qty'],
                precision_rounding=rounding)

            res[product_id]['reserved_qty'] = reserved_quantity
            res[product_id]['temporary_reserved_qty'] = temporary_reserved_qty

        return res

    # Dats: Product View Remove Temp Reserve [End]
