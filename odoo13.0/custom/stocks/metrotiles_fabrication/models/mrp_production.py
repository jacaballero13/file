from odoo import models, fields, api, _
from odoo.exceptions import UserError

class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    def name_get(self):
        def map_display_name(component):
            return component.product_id.display_name

        if self._context.get('stock_scrap_bom'):
            return [(bom.id, '%s%s' % (bom.code and '%s: ' % bom.code or '', ','.join(map(map_display_name, bom.bom_line_ids))))
                    for bom in self]
        elif self._context.get('picking_to_frabricate'):
            return [(bom.id, '%s%s' % (bom.code and '%s: ' % bom.code or '', ','.join(map(map_display_name, bom.bom_line_ids))))
                    for bom in self]
        else:
            return [(bom.id, '%s%s' % (bom.code and '%s: ' % bom.code or '', bom.product_tmpl_id.display_name)) for bom in self]

class MrpProduction(models.Model):
    """ Manufacturing Orders """
    _inherit = 'mrp.production'
    scrap_id = fields.Integer()
    fabricate = fields.Integer()

    @api.onchange('bom_id')
    def _onchange_bom_id(self):
        self.product_qty = self.bom_id.product_qty if self.product_qty is 0 else self.product_qty
        self.product_uom_id = self.bom_id.product_uom_id.id if self.product_qty is not self.product_uom_id else self.product_uom_id
        self.move_raw_ids = [(2, move.id) for move in self.move_raw_ids.filtered(lambda m: m.bom_line_id)] if len(
            self.move_raw_ids) <= 0 else self.move_raw_ids
        self.picking_type_id = self.bom_id.picking_type_id or self.picking_type_id

    def create_from_scrap_line(self, scrap_line, param):
        res = self.create({
                'origin': param.picking_id.name,
                'product_id': param.product_cut_size.id,
                'product_qty': param.scrap_qty,
                'product_uom_id': param.product_uom_id.id,
                'bom_id': param.bom.id,
                'picking_type_id': scrap_line.warehouse_id.manu_type_id.id,
                'location_src_id': scrap_line.warehouse_id.lot_stock_id.id,
                'location_dest_id': scrap_line.warehouse_id.lot_stock_id.id,
                'scrap_id': param.id,
            })

        res._onchange_bom_id()
        res._onchange_move_raw()
        res._onchange_location()
        # res.onchange_picking_type()
        # res.action_confirm() # mark as todo to
        res.action_assign() # reserve the components needed

    def create_picking_to_fabricate(self, to_fabricate, param):
        res = self.create({
            'origin': param.name,
            'product_id': to_fabricate.product_cut_size.id,
            'product_qty': to_fabricate.product_uom_qty,
            'product_uom_id': to_fabricate.product_uom.id,
            'bom_id': to_fabricate.bom.id,
            'picking_type_id': param.picking_type_id.warehouse_id.manu_type_id.id,
            'location_src_id': param.picking_type_id.warehouse_id.lot_stock_id.id,
            'location_dest_id': param.picking_type_id.warehouse_id.lot_stock_id.id,
            'fabricate': param.id,
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

        if self.scrap_id:
            so = self.sudo().env['stock.scrap'].search([('id', '=', self.scrap_id)])
            so.action_fabricate()
            
        if self.fabricate:
            so = self.sudo().env['stock.picking'].search([('id', '=', self.fabricate)])
            so.button_validate()
        return 