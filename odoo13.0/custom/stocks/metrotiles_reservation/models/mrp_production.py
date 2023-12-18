from odoo import models, fields, api, _
from odoo.exceptions import UserError

class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    def name_get(self):
        def map_display_name(component):
            return component.product_id.display_name

        if self._context.get('sale_order_line_bom'):
            return [(bom.id, '%s%s' % (bom.code and '%s: ' % bom.code or '', ','.join(map(map_display_name, bom.bom_line_ids))))
                    for bom in self]
        else:
            return [(bom.id, '%s%s' % (bom.code and '%s: ' % bom.code or '', bom.product_tmpl_id.display_name)) for bom in self]

class MrpProduction(models.Model):
    """ Manufacturing Orders """
    _inherit = 'mrp.production'
    sale_order_id = fields.Integer()

    @api.onchange('bom_id')
    def _onchange_bom_id(self):
        self.product_qty = self.bom_id.product_qty if self.product_qty is 0 else self.product_qty
        self.product_uom_id = self.bom_id.product_uom_id.id if self.product_qty is not self.product_uom_id else self.product_uom_id
        self.move_raw_ids = [(2, move.id) for move in self.move_raw_ids.filtered(lambda m: m.bom_line_id)] if len(
            self.move_raw_ids) <= 0 else self.move_raw_ids
        self.picking_type_id = self.bom_id.picking_type_id or self.picking_type_id

    def create_from_so_line(self, so_line):
        res = self.create({
                    'origin': so_line.order_id.name,
                    'cutting_attached': so_line.cutting_attached,
                    'product_id': so_line.product_id.id,
                    'product_qty': so_line.product_uom_qty,
                    'product_uom_id': so_line.product_uom.id,
                    'bom_id': so_line.bom.id,
                    'picking_type_id': so_line.warehouse_id.manu_type_id.id,
                    'location_src_id': so_line.warehouse_id.lot_stock_id.id,
                    'location_dest_id': so_line.warehouse_id.lot_stock_id.id,
                    'sale_order_id': so_line.order_id.id
                })

        res._onchange_bom_id()
        res._onchange_move_raw()
        res._onchange_location()
        # res.onchange_picking_type()
        # res.action_confirm() # mark as todo to
        res.action_assign() # reserve the components needed

    def button_mark_done(self):
        self.ensure_one()
        self._check_company()

        for wo in self.workorder_ids:
            if wo.time_ids.filtered(lambda x: (not x.date_end) and (x.loss_type in ('productive', 'performance'))):
                raise UserError(_('Work order %s is still running') % wo.name)
        self._check_lots()

        self.post_inventory()
        # Moves without quantity done are not posted => set them as done instead of canceling. In
        # case the user edits the MO later on and sets some consumed quantity on those, we do not
        # want the move lines to be canceled.
        (self.move_raw_ids | self.move_finished_ids).filtered(lambda x: x.state not in ('done', 'cancel')).write({
            'state': 'done',
            'product_uom_qty': 0.0,
        })

        if self.sale_order_id:
            so = self.sudo().env['sale.order'].search([('id', '=', self.sale_order_id)])
            so._action_confirm()

        return self.write({'date_finished': fields.Datetime.now()})