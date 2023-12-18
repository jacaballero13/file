from odoo import models, fields, api, exceptions, _
from odoo.tools import float_compare
import base64
from odoo.exceptions import UserError, ValidationError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    qty_available = fields.Integer(
        string="Qty Available", compute='get_remaining_stock_sale')
    order_id = fields.Many2one('sale.order', string='Order Reference',
                               required=True, ondelete='cascade', index=True, copy=False)
    branch_id = fields.Many2one(comodel_name='res.branch',
                                )
    pallet_id = fields.Many2one(
        'stock.pallet', string="Pallet Stock", required=False)
    package_id = fields.Many2one(
        'stock.quant.package', string="Pallet", required=False,)

    @api.onchange('factory_id')
    def get_branch_id(self):
        for rec in self:
            rec.branch_id = rec.order_id.warehouse_id.branch_id.id

    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            if values.get('display_type', self.default_get(['display_type'])['display_type']):
                values.update(product_id=False, price_unit=0,
                              product_uom_qty=0, product_uom=False, customer_lead=0)

            values.update(self._prepare_add_missing_fields(values))

        lines = super().create(vals_list)

        for line in lines:
            if not line.display_type and not line.order_id.is_a_version:
                if not line.to_fabricate:
                    line.calculate_rif()
                else:
                    line.calculate_rif_fab(line)

            if line.product_id and line.order_id.state == 'sale':
                msg = _("Extra line with %s ") % (
                    line.product_id.display_name,)
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
            precision = self.env['decimal.precision'].precision_get(
                'Product Unit of Measure')
            self.filtered(
                lambda r: r.state == 'sale' and float_compare(r.product_uom_qty, values['product_uom_qty'],
                                                              precision_digits=precision) != 0)._update_line_quantity(
                values)

        # Prevent writing on a locked SO.
        protected_fields = self._get_protected_fields()
        if 'done' in self.mapped('order_id.state') and any(f in values.keys() for f in protected_fields):
            protected_fields_modified = list(
                set(protected_fields) & set(values.keys()))
            fields = self.env['ir.model.fields'].search([
                ('name', 'in', protected_fields_modified), ('model', '=', self._name)
            ])
            raise exceptions.UserError(
                _('It is forbidden to modify the following fields in a locked order:\n%s')
                % '\n'.join(fields.mapped('field_description'))
            )

        prev_qty = self.product_uom_qty
        prev_product_id = self.product_id
        # temp_reserve = self.temp_reserved Dats: Remove temp reserve
        prev_bom = self.bom

        result = super(SaleOrderLine, self).write(values)

        if not self.to_fabricate:
            if prev_qty != self.product_uom_qty or prev_product_id != self.product_id:
                self.calculate_rif(
                    prev_product=prev_product_id, prev_qty=prev_qty)
        elif prev_bom.id == self.bom.id and prev_bom.id and self.bom.id and prev_qty != self.product_uom_qty:
            self.calculate_rif_fab(self, prev_qty=prev_qty, prev_bom=prev_bom)

        return result

    def get_available_qty(self):
        # Dats Refractor:
        total_onhand = 0
        location = self.sudo().env['stock.location'].search(
            [('branch_id', '=', self.order_id.warehouse_id.branch_id.id)])
        for rec in self:
            for ids in location:
                stock_quant = self.sudo().env['stock.quant'].search(
                    [('product_id', '=', self.product_id.id), ('location_id', '=', ids.id)])
                for stocks in stock_quant:
                    total_onhand += stocks.qty_available
            rec.qty_available = total_onhand
        # Dats end:
        # return (self.quantity - self.reserved_quantity) - self.temp_reserved

    def calculate_rif(self, prev_product=None, prev_qty=0):
        for rec in self:
            if not rec.to_fabricate:
                # Compute product on_hand start
                reserved_qty = 0
                temporary_reserved_qty = 0
                total_qty_onhand = 0
                on_hand = 0
                stock_quant = rec.env['stock.quant'].search(
                [('product_id', '=', rec.product_id.id), ('location_id.usage', '=', 'internal'),('location_id.name','!=','Output'),
                ('location_id.name','!=','BREAKAGE'),('location_id.name','!=','Packing Zone')])
                
                temp_reserved = rec.env['metrotiles.product.temp.reserved'].search([('product_id', '=', rec.product_id.id),])

                for stocks in stock_quant:
                    if stocks.quantity > 0:
                        total_qty_onhand += stocks.quantity
                        reserved_qty += stocks.reserved_quantity

                for temp in temp_reserved:
                    if temp.sale_line_id.id != rec.id:
                        temporary_reserved_qty+=temp.quantity
                    
                total = total_qty_onhand - reserved_qty - temporary_reserved_qty
                
                on_hand = total
                # Compute product on_hand end
                
                # Dats: Changed stock location from package to warehouse(branch)
                stock_location = rec.package_id.location_id
                # stock_location = self.warehouse_id.branch_id Dats: Commented

                # Dats: Remove temp reserve
                rec.remove_temp_reserved(
                    stock_location, prev_product, rec.temp_reserved, rec.package_id)
                """
                    CALCULATE Reserve and indent
                """
                # Dats: Get all stocks of product using selected warehouse
                # stock_quant = self.sudo().env['stock.quant'].search(
                #     [('product_id', '=', self.product_id.id), ('location_id', '=', stock_location)])
                # avail_stock = stock_quant.get_available_qty()

                # stock_diff = avail_stock - self.product_uom_qty
                stock_diff = total -rec.product_uom_qty
                # Dats end

                to_temp_reserve = 0
                to_indent = 0
                if stock_diff < 0:
                    to_indent = abs(stock_diff)

                to_temp_reserve = rec.product_uom_qty - to_indent
                rec.add_temp_reserved(
                    stock_location, rec.product_id, to_temp_reserve, rec.package_id.id)
                rec.update(
                    {'temp_reserved': to_temp_reserve, 'indent': to_indent})
                rec.update_product_temp_reserved()

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

                raw_mat_qty = self.make_raw_mat_qty_to_whole_number(
                    prev_qty, line.bom.product_qty)

                stock.update_temp_reserved(raw_mat_qty, False)
                line.temp_reserved = 0

        for component in line.bom.bom_line_ids:
            stock = self.env['stock.quant'].sudo().search([
                ('location_id', '=', self.package_id.id),
                ('product_id', '=', component.product_id.id)
            ])

            if stock.id:

                avail_stock = stock.get_available()

                raw_mat_qty = self.make_raw_mat_qty_to_whole_number(
                    line.product_uom_qty, line.bom.product_qty)

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

                line.update({'temp_reserved': reserved, 'indent': indent})

    @api.depends('temp_reserved', 'indent')
    def get_rif(self):
        for rec in self:
            fab_quant = rec.product_uom_qty if rec.bom.id else 0

            rec.rif = '{}|{}|{}'.format(
                rec.temp_reserved, rec.indent, fab_quant)

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
                     ('stock_location_id', '=', location_id.id),
                     ('package_id', '=', self.package_id.id),
                     ('is_for_fabrication', '=', False)])

                if not product_temp_reserved.id:
                    product_temp_reserved.create(
                        {'sale_line_id': self.id, 'stock_location_id': location_id.id, 'product_id': self.product_id.id,
                         'quantity': line.temp_reserved, 'package_id': self.package_id.id})
                else:
                    product_temp_reserved.update(
                        {'quantity': line.temp_reserved})

            else:
                product_temp_reserved = self.product_temp_reserved.search(
                    [('sale_line_id', '=', self.id),
                     ('stock_location_id', '=', location_id.id),
                     ('package_id', '=', self.package_id.id),
                     ('is_for_fabrication', '=', False)])

                product_temp_reserved.unlink()

    def add_temp_reserved(self, stock_location, product, qty, package=None):
        if product.id and qty > 0:
            stock_quant = self.sudo().env['stock.quant'].get_by_location_and_product(
                stock_location, product, package)
            for lines in stock_quant:
                lines.update_temp_reserved(qty)

    def unlink(self):
        if self._check_line_unlink():
            raise exceptions.UserError(_(
                'You can not remove an order line once the sales order is confirmed.\nYou should rather set the quantity to 0.'))

        for lines in self:
            if lines.state == 'draft':
                temp_reserved = self.env['metrotiles.product.temp.reserved'].search(
                    [('order_name', '=', lines.order_id.name), ('sale_line_id', '=', lines.id), ('product_id', '=', lines.product_id.id)])
                if temp_reserved:
                    temp_reserved.unlink()

        for rec in self:
            if rec.to_fabricate:
                pass
                # rec.removed_bom_component_stock_reserved(rec, rec.bom, rec.temp_reserved, rec.package_id)
            # Dats Removed unlink method for temp_reserve(error)
            # else:
            #     temp_reserved = self.env['metrotiles.product.temp.reserved'].search([('order_name','=', rec.order_id.name), ('package_id','=', rec.package_id.id), \
            #                                     ('sale_line_id','=', rec.id), ('product_id','=', rec.product_id.id)])
            #     if temp_reserved:
            #         temp_reserved.unlink()
                # rec.remove_temp_reserved(rec.get_warehouse_stock_location(), rec.product_id, rec.temp_reserved, rec.package_id)

        res = super(SaleOrderLine, self).unlink()

        return res

    def remove_temp_reserved(self, stock_location, product, qty, package):
        if product is None:
            return

        if product.id and qty > 0:
            stock_quant = self.sudo().env['stock.quant'].get_by_location_and_product(
                stock_location, product, package)

            stock_quant.update_temp_reserved(qty, isAdd=False)

    @api.depends('product_id')
    def get_remaining_stock_sale(self):
        reserved_qty = 0
        temporary_reserved_qty = 0
        total_qty_onhand = 0
        on_hand = 0
        for rec in self:

            stock_quant = self.env['stock.quant'].search(
                [('product_id', '=', rec.product_id.id), ('location_id.usage', '=', 'internal'),('location_id.name','!=','Output'),
                ('location_id.name','!=','BREAKAGE'),('location_id.name','!=','Packing Zone')])
            
            temp_reserved = self.env['metrotiles.product.temp.reserved'].search([('product_id', '=', rec.product_id.id)])

            for stocks in stock_quant:
                if stocks.quantity > 0:
                    total_qty_onhand += stocks.quantity
                    reserved_qty += stocks.reserved_quantity

            for temp in temp_reserved:
                temporary_reserved_qty+=temp.quantity
                
            total = total_qty_onhand - reserved_qty - temporary_reserved_qty
            
            on_hand = total
        
            rec.qty_available = on_hand