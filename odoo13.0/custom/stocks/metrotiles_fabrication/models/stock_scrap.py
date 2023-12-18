
from odoo import models, api, fields, _



class StockScrap(models.Model):
    _inherit = 'stock.scrap'
    # Method for the wizard Fabricate
    
    
    bom = fields.Many2one('mrp.bom', string="BOM")
    bom_display_name = fields.Char(string="Components", compute="get_bom_display_name")

    product_cut_size = fields.Many2one('product.product', compute="get_bom_display_name", string="BOM Product ")
    state = fields.Selection(selection_add=[('fabricate', 'Fabricated')])

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
    def action_fabricate(self):
        for rec in self:
            for pick in rec.picking_id:
                for scrap in pick.picking_type_id:
                    test = self.env['mrp.production'].sudo().create_from_scrap_line(scrap_line=scrap, param=rec)
                    print(test)
        return self.write({'state': 'fabricate'})

