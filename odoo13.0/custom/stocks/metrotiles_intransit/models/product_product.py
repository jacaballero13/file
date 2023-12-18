# -*- coding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID, _
from datetime import datetime
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = 'product.product'
    
    
    incoming_shipments = fields.Float(
        string='In Transit',
        store = True,
    )
    
    
class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        quantity_done = 0
        qty_done = 0
        for stock_move in self.move_ids_without_package:
            product_id = stock_move['product_id']
            quantity_done = stock_move.product_uom_qty
            if quantity_done >= 0 or 0.00:
                product_id = self.env['product.product'].search([('id', '=', product_id.id)])
                for product in product_id:
                    if product.incoming_shipments >= quantity_done:
                        intransit_qty = product.incoming_shipments
                        product.update({'incoming_shipments': intransit_qty - quantity_done })
                        break
                
        for stock_move_line in self.move_line_nosuggest_ids:
            product_id = stock_move_line.product_id.id
            qty_done   = stock_move_line.qty_done
            product_id = self.env['product.product'].search([('id', '=', product_id)])
            if product_id.incoming_shipments >= quantity_done:
                intransit_qty = product_id.incoming_shipments
                product_id.update({'incoming_shipments': intransit_qty - qty_done})
                break

        return res
    
    # def action_cancel(self):
    #     res = super(StockPicking, self).action_cancel()
    #     quantity_done = 0
    #     for move in self.move_ids_without_package:
    #         if move.quantity_done > 0 and self.picking_type_id.name == 'RECEIVING':
    #             product_id = move['product_id']
    #             quantity_done = move.product_uom_qty
    #             product_ids = self.env['product.product'].sudo().search([('id', '=', product_id.id)])
    #             for product in product_ids:
    #                 if product.incoming_shipments >= quantity_done:
    #                     intransit_qty = product.incoming_shipments if product.incoming_shipments > 0 else None
    #                     product.update({'incoming_shipments': intransit_qty - quantity_done})
    #                     break
    #     return res
