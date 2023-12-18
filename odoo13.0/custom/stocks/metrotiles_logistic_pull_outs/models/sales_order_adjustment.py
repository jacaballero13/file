from odoo import models, fields, api
from odoo.exceptions import UserError

class MetrotilesSalesOrderAdjustments(models.Model):
    _inherit = 'sales.order.adjustment'

    
    def button_approved4(self):
        pull_outs_obj = self.env['metrotiles.pull.outs']
        for rec in self:
            for warehouse in rec.sale_order_id.warehouse_id:
                picking_out_ids = self.env['stock.picking'].search([('origin','=',rec.sale_order_id.name), ('state', '=', 'done'), ('picking_type_id', '=', warehouse.out_type_id.id)])
                if picking_out_ids and rec.adjustment_type == 'change_qty':
                    change_quants_lines = [(5,0,0,)]
                    for change_quants in rec.change_quantity_lines:
                        if change_quants.new_qty > 0 and len(change_quants) > 0:
                            change_quants_lines.append((0,0,{
                                'location_id': change_quants.location_id.id,
                                'application_id': change_quants.application_id.id,
                                'factory_id': change_quants.factory_id.id,
                                'series_id': change_quants.series_id.id,
                                'product_id': change_quants.product_id.id,
                                'size': change_quants.size,
                                'variant': change_quants.variant,
                                'product_uom_qty': change_quants.new_qty,
                                'qty_delivered': change_quants.qty_delivered,
                                'pull_out_qty': change_quants.qty_delivered-change_quants.new_qty,
                            }))
                    pull_outs_obj.create({
                        'sale_order_id': rec.sale_order_id.id,
                        'partner_id': rec.partner_id.id,
                        'pullout_type': 'saf', 
                        'pu_order_lines': change_quants_lines,
                    })
                    rec.state = 'approved'
        
        return super(MetrotilesSalesOrderAdjustments,self).button_approved4()