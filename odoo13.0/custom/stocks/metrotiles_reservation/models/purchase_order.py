from odoo import models, fields, api, exceptions, _


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    quantity = fields.Float('Quantity', compute="_get_po_line_qty")
    indention_id = fields.Many2one('metrotiles.sale.indention', string="Purchase Order Line")
    size = fields.Char(store=True)

    @api.onchange('indention_id')
    def indention_id_changed(self):
        for rec in self:
            if rec.indention_id:
                rec.product_id = rec.indention_id.product_id.id,
            rec.update({
                
                'product_qty': rec.indention_id.balance
            })

    def _suggest_quantity(self):
        '''
        Suggest a minimal quantity based on the seller
        '''
        if not self.indention_id.id:
            if not self.product_id:
                return
            seller_min_qty = self.product_id.seller_ids \
                .filtered(
                lambda r: r.name == self.order_id.partner_id and (not r.product_id or r.product_id == self.product_id)) \
                .sorted(key=lambda r: r.min_qty)
            if seller_min_qty:
                self.product_qty = seller_min_qty[0].min_qty or 1.0
                self.product_uom = seller_min_qty[0].product_uom
            else:
                self.product_qty = 1.0
        else:
            self.product_qty = self.indention_id.balance

    @api.model
    def create(self, values):
        if values.get('display_type', self.default_get(['display_type'])['display_type']):
            values.update(product_id=False, price_unit=0, product_uom_qty=0, product_uom=False, date_planned=False)

        order_id = values.get('order_id')

        if 'date_planned' not in values:
            order = self.env['purchase.order'].browse(order_id)
            if order.date_planned:
                values['date_planned'] = order.date_planned
        line = super(PurchaseOrderLine, self).create(values)

        if line.order_id.state == 'purchase':
            msg = _("Extra line with %s ") % (line.product_id.display_name,)
            line.order_id.message_post(body=msg)

        return line

    def validate_contract_indent_balance(self):
        if self.indention_id.balance < 0:
            pass
            # raise exceptions.UserError(
            #     _('Cannot set quantity that is greater than contract \'%s\' Indent balance'
            #       '\n- Balance \'%s\'')
            #     % (self.indention_id.name, self.indention_id.balance))

    @api.model
    def create(self, values):
        if values.get('display_type', self.default_get(['display_type'])['display_type']):
            values.update(product_id=False, price_unit=0, product_uom_qty=0, product_uom=False, date_planned=False)

        order_id = values.get('order_id')
        if 'date_planned' not in values:
            order = self.env['purchase.order'].browse(order_id)
            if order.date_planned:
                values['date_planned'] = order.date_planned

        line = super(PurchaseOrderLine, self).create(values)

        if line.order_id.state == 'purchase':
            msg = _("Extra line with %s ") % (line.product_id.display_name,)
            line.order_id.message_post(body=msg)

        line.validate_contract_indent_balance()

        return line

    def write(self, values):
        if 'display_type' in values and self.filtered(lambda line: line.display_type != values.get('display_type')):
            raise UserError("You cannot change the type of a purchase order line. Instead you should delete the current line and create a new line of the proper type.")

        if 'product_qty' in values:
            for line in self:
                if line.order_id.state == 'purchase':
                    line.order_id.message_post_with_view('purchase.track_po_line_template',
                                                         values={'line': line, 'product_qty': values['product_qty']},
                                                         subtype_id=self.env.ref('mail.mt_note').id)


        prev_indention = self.indention_id

        is_updated = super(PurchaseOrderLine, self).write(values)

        # Re-calculate previous indention balance
        if values.get('product_qty') and not values.get('indention_id'):
            prev_indention.count_balance()

        # Validate Contract Indent Balance
        if values.get('product_qty') or values.get('indention_id'):
            self.validate_contract_indent_balance()

        return is_updated

    def unlink(self):
        indention_id = None

        for line in self:
            if line.indention_id.id:
                indention_id = line.indention_id

            if line.order_id.state in ['purchase', 'done']:
                raise exceptions.UserError(_('Cannot delete a purchase order line which is in state \'%s\'.') % (line.state,))

        is_deleted = super(PurchaseOrderLine, self).unlink()

        if is_deleted and indention_id:
            indention_id.count_balance()

        return is_deleted

