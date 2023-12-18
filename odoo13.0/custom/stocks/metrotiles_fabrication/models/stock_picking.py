
from odoo import api, models, fields



class StockMove(models.Model):
    _inherit = 'stock.move'
    
    
    bom = fields.Many2one('mrp.bom', string="BOM")
    bom_display_name = fields.Char(string="Components", compute="get_bom_display_name")
    activate = fields.Boolean('Fabricate')
    product_cut_size = fields.Many2one('product.product', compute="get_bom_display_name", string="BOM Product ")
    
    @api.depends('bom')
    def get_bom_display_name(self):
        bom_product_id = False
        for rec in self:
            display_name = []

            if rec.bom.id:
                bom_product_id = rec.bom.product_id.id
                for component in rec.bom.bom_line_ids:
                    display_name.append(component.product_id.display_name)

            else:
                rec.bom_display_name = ''

            rec.bom_display_name = ','.join(display_name)
            rec.product_cut_size = bom_product_id
    
class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    
    def action_approve(self):
        for rec in self:
            for fabricate in rec.move_ids_without_package:
                if fabricate.activate and self.picking_type_code == 'incoming':
                    test = self.env['mrp.production'].sudo().create_picking_to_fabricate(to_fabricate=fabricate, param=rec)
                    print(test)
        return super(StockPicking, self).action_approve()


