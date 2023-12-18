from odoo import fields, models, api, _
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    indent_created = fields.Boolean(default=False)

    def open_indent_wizard(self):
        return {
            'name': _('Picking Indent'),
            'res_model': 'indent.picking.wizard',
            'view_mode': 'form',
            'context': {
                'active_model': 'stock.picking',
                'active_ids': self.ids,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }
        
    # def create_indent_from_picking(self):
    #     for rec in self:
    #         for lines in rec.move_ids_without_package:
    #             if lines.product_uom_qty != lines.quantity_done:
    #                 indent_qty = (lines.product_uom_qty - lines.quantity_done)
    #                 rec.env['metrotiles.sale.indention'].sudo().create({
    #                     'quantity': indent_qty,
    #                     'sale_line_id': False,
    #                     'factory_id': lines.product_id.factory_id.id,
    #                     'to_fabricate': False,
    #                     'fabricate_line_id': False,
    #                     'move_picking_id': lines.id
    #                 })
    #         rec.update({'indent_created': True})
        
    #     message = {
    #         'type': 'ir.actions.client',
    #         'tag': 'display_notification',
    #         'params': {
    #                 'title': 'Success',
    #                 'message': 'Created Indention for this picking.',
    #                 'sticky': False,
    #                 'next': {'type': 'ir.actions.act_window_close'},
    #         }
    #     }
    #     return message