from odoo import fields, api, models, _
from odoo.exceptions import ValidationError


class MrpProduction(models.Model):
    _inherit = 'mrp.production'
    
    has_indent = fields.Boolean(default=False)
    indent_created = fields.Boolean(default=False)
    
    
    
    def action_assign(self):
        res = super(MrpProduction, self).action_assign()
        for rec in self:
            indent_qty = 0
            for lines in rec.move_raw_ids:
                if lines.reserved_availability < lines.product_uom_qty:
                    indent_qty += (lines.product_uom_qty - lines.reserved_availability)
                    
            if indent_qty > 0:
                rec.update({'has_indent': True})
            
            elif indent_qty == 0:
                rec.update({'has_indent': False})
            
            # for temp reserved
            sale_id = self.env['sale.order'].search(
                [('name', '=', rec.origin)])

            sale_order_line = self.env['sale.order.line'].search(
                [('order_id', '=', sale_id.id),('product_id','=', rec.product_id.id),('product_uom_qty','=',rec.product_qty)],limit=1)
            
            # Temporarily removed: will fix after pending work
            # if sale_order_line:
            #     for lines in rec.move_raw_ids:
            #         for bom in sale_order_line.bom.bom_line_ids:
            #             if bom.product_id == lines.product_id:
            #                 self.env['metrotiles.product.temp.reserved'].sudo().create({
            #                     'stock_location_id': 15,
            #                     'quantity': lines.reserved_availability,
            #                     'sale_line_id': sale_order_line.id,
            #                     'product_id': lines.product_id.id,
            #                 })
            
        return res
    
    
    def create_indent_from_mrp(self):
        for rec in self:
            for lines in rec.move_raw_ids:
                if lines.reserved_availability < lines.product_uom_qty:
                    indent_qty = (lines.product_uom_qty - lines.reserved_availability)
                    rec.env['metrotiles.sale.indention'].sudo().create({
                        'quantity': indent_qty,
                        'sale_line_id': None,
                        'factory_id': lines.product_id.factory_id.id,
                        'to_fabricate': False,
                        'fabricate_line_id': lines.id
                    })
            rec.update({'indent_created': True})
        