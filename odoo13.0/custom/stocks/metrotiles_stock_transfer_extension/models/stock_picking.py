from odoo import models, fields, api, _
from odoo.exceptions import UserError

class StockPickingInherit(models.Model):
    _inherit = 'stock.picking'
    
    def transfer_confirm(self):
        line = []
        for rec in self:
            for prod in rec.move_lines:
                
                line.append((0,0,{
                    'product_id': prod.product_id.id,
                    'product_uom_qty': prod.product_uom_qty,
                    'product_uom': prod.product_uom.id,
                    'quantity_done': prod.product_uom_qty,
                    'name': prod.product_id.name,
                    'state': 'assigned'
                }))
            receipt_obj = self.env['stock.picking.type'].search([('default_location_dest_id','=',rec.location_dest_id.id),('code','=', 'incoming')])
            default=None
            default = dict(default or {})
            self.ensure_one()
            default.update({
                'picking_type_id': receipt_obj.id,
                'move_lines':line,
                'scheduled_date': fields.Datetime.now()
            })
        self.write({'is_locked': False,
                    'state': 'done'})
        self.copy(default)

    