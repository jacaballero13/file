
from os import read
from odoo import api, models, fields



class MetrotilesStockScrapWizard(models.Model):
    _name = 'metrotiles_stocks.scrap_wizard'
    _description = "This will add on Action Server for Srap Models"
    
    picking_id = fields.Many2one('stock.picking', string="Reference", readonly=True)
    bom = fields.Many2one('mrp.bom', string="BOM")
    bom_display_name = fields.Char(string="Components", compute="get_bom_display_name")

    scrap_id = fields.Many2one('Srap')
    product_id = fields.Many2one('product.product', string="Product", readonly=True)
    product_uom_qty = fields.Float('Product Qty')
    
    
    @api.depends('bom')
    def get_bom_display_name(self):
        for rec in self:
            display_name = []

            if rec.bom.id:

                for component in rec.bom.bom_line_ids:
                    display_name.append(component.product_id.display_name)

            else:
                rec.bom_display_name = ''

            rec.bom_display_name = ','.join(display_name)
            
    def action_fabricate(self):
        for rec in self:
            for pick in rec.picking_id.picking_type_id.warehouse_id:
                self.env['mrp.production'].sudo().create_from_scrap_line(scrap_line=pick)
            self._action_fabricate()
        return