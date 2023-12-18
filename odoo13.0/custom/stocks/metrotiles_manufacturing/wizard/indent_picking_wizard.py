
from odoo import models, fields, api


class IndentPickingWizard(models.TransientModel):
    _name = 'indent.picking.wizard'
    
    stock_move_ids = fields.One2many(comodel_name='indent.picking.wizard.lines', inverse_name='picking_wizard_id')
    
    @api.model
    def default_get(self, vals):
        res = super(IndentPickingWizard, self).default_get(vals)
        stock_moves = []
        active_model = self._context.get('active_model')
        active_ids = self._context.get('active_ids')
        stock_pick_obj = self.env[active_model].browse(active_ids)

        for moves in stock_pick_obj.move_ids_without_package:
            stock_moves.append((0, 0, {
                                'move_id': moves.id,
                                'product_id': moves.product_id.id,
                                'factory_id': moves.factory_id.id,
                                'series_id': moves.series_id.id,
                                'variant': moves.variant,
                                'sizes': moves.size,
                                'demand_qty': moves.product_uom_qty,
                                }))

        res.update({'stock_move_ids': stock_moves,})

        return res

    def create_indent_from_picking(self):
        active_model = self._context.get('active_model')
        active_ids = self._context.get('active_ids')
        stock_pick_obj = self.env[active_model].browse(active_ids)
        for rec in self:
            for lines in rec.stock_move_ids:
                product_to_indent = False if lines.indent_type == 'cut_size' else lines.raw_matt_id.id
                if lines.qty_to_indent>0:
                    rec.env['metrotiles.sale.indention'].sudo().create({
                        'quantity': lines.qty_to_indent,
                        'sale_line_id': False,
                        'factory_id': lines.factory_id.id,
                        'to_fabricate': False,
                        'fabricate_line_id': False,
                        'move_picking_id': lines.move_id.id,
                        'raw_matt_product_id': product_to_indent
                    })
            stock_pick_obj.update({'indent_created': True})
        
        message = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                    'title': 'Success',
                    'message': 'Created Indention for this picking.',
                    'sticky': False,
                    'next': {'type': 'ir.actions.act_window_close'},
            }
        }
        return message


class IndentPickingWizardLines(models.TransientModel):
    _name = 'indent.picking.wizard.lines'
    
    picking_wizard_id = fields.Many2one(comodel_name='indent.picking.wizard')
    move_id = fields.Many2one(comodel_name='stock.move')
    product_id = fields.Many2one(comodel_name='product.product')
    factory_id = fields.Many2one(comodel_name='res.partner')
    series_id = fields.Many2one(comodel_name='metrotiles.series')
    variant = fields.Char()
    sizes = fields.Char()
    demand_qty = fields.Float(string="Demand Qty")
    indent_type = fields.Selection(selection=[('cut_size', "Cut Size"),
                                              ('raw_matt', "Raw Matt")])
    raw_matt_id = fields.Many2one(comodel_name='product.product')
    qty_to_indent = fields.Float(string="Qty to indent")