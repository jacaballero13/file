# -*- coding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    cutting_attached = fields.Binary(
        string='Add Attachment',
    )
    requested_qty = fields.Integer(string="Requested Qty", copy=False)
    picked_qty = fields.Integer(
        string="Picked Qty", compute='compute_qty_request')

    @api.depends('product_id', 'order_id')
    def compute_qty_request(self):
        for rec in self:

            picking_id = self.env['stock.picking'].search(
                [('origin', '=', self.order_id.name), ('picking_type_id.name', '=', 'PICK'), ('state', '=', 'done')])

            so_id = rec.env['sale.order'].search(
                [('id', '=', rec.order_id.id)])
            rec.picked_qty = 0
            pick_qty = 0
            request = 0
            diff = 0

                  
            if picking_id:

                for pick in picking_id.move_ids_without_package:
                    pick_qty += pick.quantity_done
                    if rec.product_id:
                        if pick.product_id.default_code == rec.product_id.default_code:
                            for so_line in so_id.order_line:
                                if pick_qty >= so_line.product_uom_qty and rec.id == so_line.id:
                                    pick_qty = pick_qty 
                            for lines in so_id.order_line:
                                if lines.id == rec.id:
                                    if rec.product_uom_qty <= pick_qty:
                                        rec.picked_qty = rec.product_uom_qty
                                    
                                    else:
                                        rec.picked_qty = pick_qty
                        elif rec.id == 547687:
                            rec.picked_qty = 10
                        elif rec.id == 17030:
                            rec.picked_qty = 16
                        elif rec.id == 348260:
                            rec.picked_qty = 6505
                        
                    else:
                        rec.picked_qty = 0
            else:
                rec.picked_qty = 0
            #temporary only fixing quotation types
            if rec.id in (651658,651200,652032,651198):
                rec.picked_qty = 1    

            if rec.id == 1039474:
                rec.picked_qty = 836

            if rec.id == 285385:
                rec.picked_qty = 8

            if rec.id in (667287,667286,667285,667284):
                rec.picked_qty = 1 

            if rec.id in (26097,26095, 761749, 981518, 981516, 981476):
                rec.picked_qty = rec.product_uom_qty

            if rec.id == 707806:
                rec.picked_qty = 0

            if rec.id in (805719,805718,1219292):
                rec.picked_qty = 0

            if rec.id == 361380:
                rec.picked_qty = rec.product_uom_qty

            if rec.id == 679807:
                rec.picked_qty = 0

            if rec.id == 907636:
                rec.picked_qty = 0

            if rec.order_id.quotation_type == 'sample':
                rec.picked_qty = rec.product_uom_qty   
