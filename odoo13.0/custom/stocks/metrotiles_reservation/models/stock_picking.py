from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError



class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    
    def button_validate(self):
        """
            : Outgoing delivery orders
            : Partial or Full Delivered items
            First Loop stock move of move_ids_without_package and get product id
                If quantity_done  < product_uom_qty
                    Update reserved qty from production reservation
                Delete product reservation if fully delivered items 
        """
        
        for move in self.move_ids_without_package:
            product_id = move.product_id.id
            reservation = self.env['metrotiles.product.reserved'].search([('product_id', '=', product_id), \
                                    ('order_name', '=', self.group_id.name)
                                    ]) 
            if self.picking_type_id.code == 'outgoing':
                if move.quantity_done == move.product_uom_qty:
                    reservation.unlink()
                else:
                    reservation.unlink()
        return super(StockPicking, self).button_validate()

