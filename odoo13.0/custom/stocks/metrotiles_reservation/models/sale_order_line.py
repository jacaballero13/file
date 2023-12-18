from odoo import models, fields, api, exceptions, _
from odoo.tools import float_compare
import base64
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    wastage = fields.Float(string='Wastage', store=True, compute="calculate_wastage_and_amount", digits=(12, 2))
    wastage_amount = fields.Float(string='Wastage Amount', store=True, compute="calculate_wastage_and_amount")

    @api.depends('order_line.wastage', 'order_line.wastage_amount', 'order_line')
    def calculate_wastage_and_amount(self):
        for rec in self:
            total_area = 0.0
            wastage_amount_total = 0.0
            wastage = 0.0

            for ol in rec.order_line:
                if ol.wastage > 0:
                    wastage_amount_total += ol.wastage_amount
                    total_area += ol.area
                    wastage += ol.area * (ol.wastage / 100)

            if wastage > 0 and total_area > 0:
                wastage = wastage / total_area

            rec.wastage = wastage * 100
            rec.wastage_amount = wastage_amount_total

    def action_confirm(self):
        # if self._get_forbidden_state_confirm() & set(self.mapped('state')):
        #     raise exceptions.UserError(_(
        #         'It is not allowed to confirm an order in the following states: %s'
        #     ) % (', '.join(self._get_forbidden_state_confirm())))

        for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
            order.message_subscribe([order.partner_id.id])

        if self.state is not 'sale':
            for line in self.order_line:
                location_id = line.pallet_id.location_id.id
                if not line.to_fabricate:
                    for prod_temp_reserve in line.product_temp_reserved:
                        # stock_loc_id = self.env['stock.quant'].search([('location_id','=', location_id), ('product_id', '=', line.product_id.id)])
                        self.env['metrotiles.product.reserved'].sudo().create({
                            'stock_location_id': location_id,
                            'package_id': line.package_id.id,
                            'quantity': prod_temp_reserve.quantity,
                            'sale_line_id': line.id,
                            'product_id': line.product_id.id,
                        })
                        prod_temp_reserve.unlink()
                else:
                    # line.remove_temp_reserved(line.warehouse_id.lot_stock_id, line.bom.bom_line_ids[0].product_id, line.temp_reserved, line.package_id.id)
                    self.env['mrp.production'].sudo().create_from_so_line(so_line=line)

                if line.indent > 0:
                    self.env['metrotiles.sale.indention'].sudo().create({
                        'quantity': line.indent,
                        'sale_line_id': line.id,
                        'factory_id': line.factory_id.id,
                        'to_fabricate': False
                    })
                # Create Indent from fabrication
                fab_quant = line.product_uom_qty if line.bom.id else 0
                if line.bom.id and line.to_fabricate:
                    self.env['metrotiles.sale.indention'].sudo().create({
                        'quantity': fab_quant,
                        'sale_line_id': line.id,
                        'factory_id': line.factory_id.id,
                        'to_fabricate': True
                    })
        self.write({
            'state': 'sale',
            'date_order': fields.Datetime.now()
        })

        self._action_confirm()

        if self.env.user.has_group('sale.group_auto_done_setting'):
            self.action_done()

        return True

    def calculate_fab_price(self, raw_net_price, raw_mat_size, fab_size):
        raw_mat_size = raw_mat_size.split('x')
        fab_size = fab_size.split('x')

        raw_mat_area = float(raw_mat_size[0]) * float(raw_mat_size[1])
        fab_area = float(fab_size[0]) * float(fab_size[1])

        return (fab_area / raw_mat_area) * raw_net_price

    @api.depends('order_line.price_subtotal', 'partner_id')
    def location_group_order_line(self):
        for rec in self:
            group = {}
            location_subtotal = []
            location_variant_group = []
            o_lines = []
            o_line_section = []

            for o_line in rec.order_line:
                if not o_line.display_type:
                    is_exist = False

                    for ol in o_lines:
                        if ol.get('product_tmpl_id') == o_line.product_id.product_tmpl_id.id \
                                and ol.get('location') == o_line.location_id.name \
                                and ol.get('application') == o_line.application_id.name \
                                and ol.get('size') == o_line.size \
                                and ol.get('price_unit') == o_line.price_unit \
                                and not ol.get('frabicated'):
                            is_exist = True

                            ol['qty'] += o_line.product_uom_qty
                            ol['price_subtotal'] += o_line.price_subtotal

                    if not is_exist:
                        discounts = None
                        for discount in o_line.discounts:
                            discounts = discount.name if not discounts else '{}, {}'.format(discounts,
                                                                                            discount.name)
                        o_lines.append({
                            'product_id': o_line.product_id.id,
                            'product_tmpl_id': o_line.product_id.product_tmpl_id.id,
                            'location': o_line.location_id.name,
                            'application': o_line.application_id.name,
                            'series_id': o_line.series_id.description_name,
                            'prod_photo': o_line.product_id,
                            'factory': o_line.factory_id.name_abbrev,
                            'product': 'to_do',
                            'product_display_name': o_line.product_id.name,
                            'qty': o_line.product_uom_qty,
                            'uom': o_line.product_uom.name,
                            'size': o_line.size,
                            'discounts': discounts,
                            'price_unit': o_line.price_unit,
                            'price_net': o_line.price_net,
                            'price_subtotal': o_line.price_subtotal,
                            'display_type': None,
                        })

                else:
                    o_line_section.append(o_line.name)

            for ol_section in o_line_section:
                subtotal = 0

                location_variant_group.append({
                    'name': ol_section,
                    'display_type': 'line_section'
                })

                for o_line in o_lines:
                    if ol_section == o_line.get('location'):
                        location_variant_group.append(o_line)
                        subtotal += o_line.get('price_subtotal')

                location_variant_group.append({
                    'amount': subtotal,
                    'display_type': 'line_total'
                })

            rec.update({
                'location_subtotal_group': [],
                'location_variant_group': location_variant_group})


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    stock_quant = fields.Many2one('stock.quant', string='Stock Quant')
    fabricate = fields.Many2one('metrotiles.fabrication.cut.size')
    temp_reserved = fields.Integer(string="Temporary Reserved", default=0)
    indent = fields.Integer(string="Indent", default=0)
    product_temp_reserved = fields.One2many('metrotiles.product.temp.reserved', 'sale_line_id',
                                            string='product_temp_reserved', ondelete='cascade')
    cut_sizes = fields.One2many('metrotiles.fabrication.cut.size', 'sale_order_line_id')
    to_fabricate = fields.Boolean('Fabricate')
    fabricated_qty = fields.Integer('Final Quantity')
    rif = fields.Char(string="RIF", default='0|0|0', compute="get_rif")

    area = fields.Float(string="Area", compute="calculate_area_wastage_amount", store=True)
    wastage_amount = fields.Float(string='Wastage Amount', store=True, default=0.0,
                                  compute="calculate_area_wastage_amount")
    wastage = fields.Float(string='Wastage %', default=0.0, store=True)

    bom = fields.Many2one('mrp.bom', string="BOM")
    bom_display_name = fields.Char(string="Components", compute="get_bom_display_name")

    package_id = fields.Many2one('stock.quant.package', string="Pallet", required=True,)
    pallet_id = fields.Many2one('stock.pallet', string="Pallet Stock", required=True)

    # price_unit = fields.Float('Unit Price', required=True, digits='Product Price', default=0.0, compute="get_lst_price")
    #
    # @api.depends('product_id')
    # def get_lst_price(self):
    #     for rec in self:
    #         rec.price_unit = rec.product_id.lst_price

    @api.onchange('pallet_id')
    def get_pallet_id(self):
        for xx in self.pallet_id:
            self.package_id = xx.pallet.id
            
    @api.depends('bom')
    def get_bom_display_name(self):
        for rec in self:
            display_name = []

            if rec.bom.id:

                for component in rec.bom.bom_line_ids:
                    display_name.append(component.product_id.display_name)

            else:
                rec.bom_display_name = ''

            rec.bom_display_name = ','.join(display_name)

    @api.depends('wastage', 'product_id')
    def calculate_area_wastage_amount(self):
        for rec in self:
            raw_material_size = rec.size.split('x') if rec.size != 'N/A' else ['0', '0']

            rec.area = eval(raw_material_size[0]) * eval(raw_material_size[0])
            rec.wastage_amount = (rec.wastage / 100) * rec.price_subtotal

    """ DELETE THIS LINE """
    # @api.onchange('stock_quant')
    # def stock_quant_changed(self):
    #     self.product_id = self.stock_quant.product_id

    def get_stock_locations_param(self):
        params = self.env['ir.config_parameter'].sudo()

        return eval(params.get_param('stock_locations', default=[]))

    @api.depends('temp_reserved', 'indent')
    def get_rif(self):
        for rec in self:
            fab_quant = rec.product_uom_qty if rec.bom.id else 0

            rec.rif = '{}|{}|{}'.format(rec.temp_reserved, rec.indent, fab_quant)

    def update_product_temp_reserved(self):
        """
            Check if reserve qty is greater than zero
                IF product product_temp_reserve exist change the quantity
                If not create new product_temp_reserve record
            Put location id to unlink product in stock quant
            If reserve qty is zero, remove product_temp_reserve record
        """
        location_id = self.sudo().pallet_id.location_id
        # stock_quant = self.env['stock.quant'].sudo().search([('location_id','=', stock.id )])
        for line in self:
            if line.temp_reserved > 0:
                product_temp_reserved = self.product_temp_reserved.search(
                    [('sale_line_id', '=', self.id),
                    ('stock_location_id','=', location_id.id),
                    ('package_id', '=', self.package_id.id ),
                    ('is_for_fabrication', '=', False)])

                if not product_temp_reserved.id:
                    product_temp_reserved.create(
                        {'sale_line_id': self.id, 'stock_location_id': location_id.id, 'product_id': self.product_id.id,
                        'quantity': line.temp_reserved, 'package_id': self.package_id.id})
                else:
                    product_temp_reserved.update({'quantity': line.temp_reserved})

            else:
                product_temp_reserved = self.product_temp_reserved.search(
                    [('sale_line_id', '=', self.id),
                    ('stock_location_id', '=', location_id.id),
                    ('package_id', '=', self.package_id.id ),
                    ('is_for_fabrication', '=', False)])
                    
                product_temp_reserved.unlink()

    def calculate_rif(self, prev_product=None, prev_qty=0):
        if not self.to_fabricate:
            stock_location = self.package_id.location_id

            self.remove_temp_reserved(stock_location, prev_product, self.temp_reserved, self.package_id)

            """
                CALCULATE Reserve and indent
            """
            stock_quant = self.sudo().env['stock.quant'].search([('product_id', '=', self.product_id.id), ('package_id', '=', self.package_id.id), ('location_id','=', stock_location.id)])
            
            avail_stock = stock_quant.get_available_qty()
            
            stock_diff = avail_stock - self.product_uom_qty
            to_temp_reserve = 0
            to_indent = 0

            if stock_diff < 0:
                to_indent = abs(stock_diff)

            to_temp_reserve = self.product_uom_qty - to_indent
            self.add_temp_reserved(stock_location, self.product_id, to_temp_reserve, self.package_id.id)
            self.update({'temp_reserved': to_temp_reserve, 'indent': to_indent})
            self.update_product_temp_reserved()

    def remove_temp_reserved(self, stock_location, product, qty, package):
        if product is None:
            return

        if product.id and qty > 0:
            stock_quant = self.sudo().env['stock.quant'].get_by_location_and_product(stock_location, product, package)

            stock_quant.update_temp_reserved(qty, isAdd=False)

    def add_temp_reserved(self, stock_location, product, qty, package):
        if product.id and qty > 0:
            stock_quant = self.sudo().env['stock.quant'].get_by_location_and_product(stock_location, product, package)
            stock_quant.update_temp_reserved(qty)


    def get_warehouse_stock_location(self):
        return self.sudo().pallet_id.location_id

    # def calculate_rif(self, line, prev_qty=0):
    #     if not line.to_fabricate:
    #         reserved = 0.0
    #         indent = 0.0
    
    #         stock = self.sudo().order_id.lot_stock_id
    
    #         if stock.id:
    #             tem_reserved = 0
    
    #             if prev_qty > 0:
    #                 tem_reserved = stock.temp_reserved - prev_qty
    #             else:
    #                 tem_reserved = stock.temp_reserved
    
    #             avail_stock = (stock.quantity - stock.reserved_quantity) - tem_reserved
    
    #             if avail_stock > 0:
    #                 diff = avail_stock - (line.product_uom_qty - reserved)
    
    #                 if diff < 0:
    #                     reserved = line.product_uom_qty + diff
    #                     stock.update({'temp_reserved': tem_reserved + reserved})
    #                 else:
    #                     reserved = line.product_uom_qty
    #                     stock.update({'temp_reserved': tem_reserved + reserved})
    
    #             line.update_product_temp_reserved(reserved, stock.location_id.id)
    
    #     indent = abs(reserved - line.product_uom_qty)
    
    #     line.update({'temp_reserved': reserved, 'indent': indent})
    #     line.product_temp_reserved

    def removed_bom_component_stock_reserved(self, line, bom, prev_qty):
        for component in bom.bom_line_ids:
            stock = self.env['stock.quant'].sudo().search([
                ('location_id', '=', self.package_id.id),
                ('product_id', '=', component.product_id.id)
            ])

            raw_mat_qty = self.make_raw_mat_qty_to_whole_number(prev_qty, bom.product_qty)

            stock.update_temp_reserved(raw_mat_qty, False)
            line.temp_reserved = 0


    def calculate_rif_fab(self, line, prev_qty=0, prev_bom=False):
        """
            Reserve all bom components
        """

        if prev_bom:
            for component in prev_bom.bom_line_ids:
                stock = self.env['stock.quant'].sudo().search([
                    ('location_id', '=', self.package_id.id),
                    ('product_id', '=', component.product_id.id)
                ])

                raw_mat_qty = self.make_raw_mat_qty_to_whole_number(prev_qty, line.bom.product_qty)

                stock.update_temp_reserved(raw_mat_qty, False)
                line.temp_reserved = 0

        for component in line.bom.bom_line_ids:
            stock = self.env['stock.quant'].sudo().search([
                ('location_id', '=', self.package_id.id),
                ('product_id', '=', component.product_id.id)
            ])

            if stock.id:

                avail_stock = stock.get_available()

                raw_mat_qty = self.make_raw_mat_qty_to_whole_number(line.product_uom_qty, line.bom.product_qty)

                diff = avail_stock - raw_mat_qty
                indent = 0
                reserved = 0

                if diff < 0:
                    indent = abs(diff)
                    reserved = raw_mat_qty - indent

                    stock.update_temp_reserved(reserved, True)
                else:
                    reserved = raw_mat_qty
                    stock.update_temp_reserved(reserved, True)

                # line.update({'temp_reserved': reserved, 'indent': indent})
                line.update({'temp_reserved': reserved, 'indent': 0})

    def make_raw_mat_qty_to_whole_number(self, product_uom_qty, bom_product_qty):
        raw_mat_qty = product_uom_qty / bom_product_qty
        has_decimal = not float(raw_mat_qty).is_integer()

        if has_decimal:
            raw_mat_qty = int(raw_mat_qty) + 1

        return raw_mat_qty

    def updateRIF(self):
        self.calculate_rif(self, self.temp_reserved)

    def fabricate_raw_material(self):
        return {
            'name': self.name,
            'res_model': 'sale.order.line',
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'view_id': self.env.ref('metrotiles_reservation.metrotiles_reservation_sale_order_line_form').id,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
        }

    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            if values.get('display_type', self.default_get(['display_type'])['display_type']):
                values.update(product_id=False, price_unit=0, product_uom_qty=0, product_uom=False, customer_lead=0)

            values.update(self._prepare_add_missing_fields(values))

        lines = super().create(vals_list)

        for line in lines:
            if not line.display_type and not line.order_id.is_a_version:
                if not line.to_fabricate:
                    line.calculate_rif()
                else:
                    line.calculate_rif_fab(line)

            if line.product_id and line.order_id.state == 'sale':
                msg = _("Extra line with %s ") % (line.product_id.display_name,)
                line.order_id.message_post(body=msg)
                # create an analytic account if at least an expense product
                if line.product_id.expense_policy not in [False, 'no'] and not line.order_id.analytic_account_id:
                    line.order_id._create_analytic_account()

        return lines

    def write(self, values):
        if 'display_type' in values and self.filtered(lambda line: line.display_type != values.get('display_type')):
            raise exceptions.UserError(_(
                "You cannot change the type of a sale order line. Instead you should delete the current line and create a new line of the proper type."))

        if 'product_uom_qty' in values:
            precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            self.filtered(
                lambda r: r.state == 'sale' and float_compare(r.product_uom_qty, values['product_uom_qty'],
                                                              precision_digits=precision) != 0)._update_line_quantity(
                values)

        # Prevent writing on a locked SO.
        protected_fields = self._get_protected_fields()
        if 'done' in self.mapped('order_id.state') and any(f in values.keys() for f in protected_fields):
            protected_fields_modified = list(set(protected_fields) & set(values.keys()))
            fields = self.env['ir.model.fields'].search([
                ('name', 'in', protected_fields_modified), ('model', '=', self._name)
            ])
            raise exceptions.UserError(
                _('It is forbidden to modify the following fields in a locked order:\n%s')
                % '\n'.join(fields.mapped('field_description'))
            )

        prev_qty = self.product_uom_qty
        prev_product_id = self.product_id
        temp_reserve = self.temp_reserved
        prev_bom = self.bom

        result = super(SaleOrderLine, self).write(values)

        if not self.to_fabricate:
            if prev_qty != self.product_uom_qty or prev_product_id != self.product_id:
                self.calculate_rif(prev_product=prev_product_id, prev_qty=prev_qty)
        elif prev_bom.id == self.bom.id and prev_bom.id and self.bom.id and prev_qty != self.product_uom_qty:
            self.calculate_rif_fab(self, prev_qty=prev_qty, prev_bom=prev_bom)

        return result

    def unlink(self):
        if self._check_line_unlink():
            raise exceptions.UserError(_(
                'You can not remove an order line once the sales order is confirmed.\nYou should rather set the quantity to 0.'))

        for rec in self:
            if rec.to_fabricate:
                pass
                # rec.removed_bom_component_stock_reserved(rec, rec.bom, rec.temp_reserved, rec.package_id)
            else:
                temp_reserved = self.env['metrotiles.product.temp.reserved'].search([('order_name','=', rec.order_id.name), ('package_id','=', rec.package_id.id), \
                                                ('sale_line_id','=', rec.id), ('product_id','=', rec.product_id.id)])
                if temp_reserved:
                    temp_reserved.unlink()
                # rec.remove_temp_reserved(rec.get_warehouse_stock_location(), rec.product_id, rec.temp_reserved, rec.package_id)

        res = super(SaleOrderLine, self).unlink()

        return res