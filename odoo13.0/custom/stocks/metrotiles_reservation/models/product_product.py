
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
from odoo.tools.float_utils import float_compare, float_is_zero, float_round

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    fabricated_product = fields.Boolean(string='Fabricated ', default=False)

class ProductProduct(models.Model):
    _inherit = 'product.product'

    temporary_reserve_ids = fields.One2many('metrotiles.product.temp.reserved', 'product_id', 'Quotation Reserved')
    contract_reserve_ids = fields.One2many('metrotiles.product.reserved', 'product_id', 'Contracts Reserved')

    reserved_qty = fields.Float(
        'Reserved', compute='_compute_quantities',
        digits='Product Unit of Measure', compute_sudo=False,
        help="Reserved Product")

    temporary_reserved_qty = fields.Float(
        'Temp. Reserved', compute='_compute_quantities',
        digits='Product Unit of Measure', compute_sudo=False,
        help="Reserved Product")

    pallet_ids = fields.One2many('stock.pallet', 'product_id', string="Pallets")

    @api.model_create_multi
    def create(self, vals_list):
        products = super(ProductProduct, self.with_context(create_product_product=True)).create(vals_list)
        # `_get_variant_id_for_combination` depends on existing variants

        warehouses = self.env['stock.warehouse'].search([])

        for product in products:
            if product.type == 'product':
                for wh in warehouses:
                    quant = self.env['stock.quant'].sudo().create({
                        'product_id': product.id,
                        'location_id': wh.lot_stock_id.id,
                        'quantity': 0,
                    })

        self.clear_caches()
        return products

    def _compute_quantities(self):
        products = self.filtered(lambda p: p.type != 'service')
        res = products._compute_quantities_dict(self._context.get('lot_id'), self._context.get('owner_id'), self._context.get('package_id'), self._context.get('from_date'), self._context.get('to_date'))

        for product in products:
            product.qty_available = res[product.id]['qty_available']
            product.incoming_qty = res[product.id]['incoming_qty']
            product.outgoing_qty = res[product.id]['outgoing_qty']
            product.virtual_available = res[product.id]['virtual_available']
            product.free_qty = res[product.id]['free_qty']
            product.reserved_qty = res[product.id]['reserved_qty']
            product.temporary_reserved_qty = res[product.id]['temporary_reserved_qty']

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

    def _compute_quantities_dict(self, lot_id, owner_id, package_id, from_date=False, to_date=False):
        domain_quant_loc, domain_move_in_loc, domain_move_out_loc = self._get_domain_locations()
        domain_quant = [('product_id', 'in', self.ids)] + domain_quant_loc
        dates_in_the_past = False
        # only to_date as to_date will correspond to qty_available
        to_date = fields.Datetime.to_datetime(to_date)
        if to_date and to_date < fields.Datetime.now():
            dates_in_the_past = True

        domain_move_in = [('product_id', 'in', self.ids)] + domain_move_in_loc
        domain_move_out = [('product_id', 'in', self.ids)] + domain_move_out_loc
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
            domain_move_in_done = [('state', '=', 'done'), ('date', '>', to_date)] + domain_move_in_done
            domain_move_out_done = [('state', '=', 'done'), ('date', '>', to_date)] + domain_move_out_done
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
                    ['qty_available', 'free_qty', 'incoming_qty', 'outgoing_qty', 'virtual_available'],
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

            reserved_quantity = quants_res.get(product_id, [False, 0.0, 0.0])[1]
            temporary_reserved_qty = quants_res.get(product_id, [False, 0.0, 0.0])[2] or 0

            res[product_id]['qty_available'] = float_round(qty_available - reserved_quantity - temporary_reserved_qty, precision_rounding=rounding)
            res[product_id]['free_qty'] = float_round(qty_available - reserved_quantity - temporary_reserved_qty, precision_rounding=rounding)
            res[product_id]['incoming_qty'] = float_round(moves_in_res.get(product_id, 0.0),
                                                          precision_rounding=rounding)
            res[product_id]['outgoing_qty'] = float_round(moves_out_res.get(product_id, 0.0),
                                                          precision_rounding=rounding)
            res[product_id]['virtual_available'] = float_round(
                (qty_available) + res[product_id]['incoming_qty'] - res[product_id]['outgoing_qty'],
                precision_rounding=rounding)

            res[product_id]['reserved_qty'] = reserved_quantity
            res[product_id]['temporary_reserved_qty'] = temporary_reserved_qty

        return res