from odoo import fields, models, api


class MetrotilesSaleIndention(models.Model):
    _inherit = 'metrotiles.sale.indention'
    
    sale_line_id = fields.Many2one(comodel_name='sale.order.line', required=False)
    fabricate_line_id = fields.Many2one(comodel_name='stock.move')
    
    po_line_id = fields.One2many('purchase.order.line', 'indention_id', string='Indent Purchase Line', domain=[('order_id.state','not in', ('cancel', 'done'))])
    factory_id = fields.Many2one('res.partner', string="Factory", required=True)
    to_purchase_qty = fields.Integer('Purchase Qty', default=0, store=True)

    contract_ref = fields.Char(compute='_compute_indent_details', string="Contract Ref.", related='')
    customer = fields.Char(compute='_compute_indent_details', string="Customer")
    product_id = fields.Many2one('product.product', string="Product", compute="get_product_id")
    series_id = fields.Many2one('metrotiles.series', compute='_compute_indent_details', string='Series')
    to_fabricate = fields.Boolean('to_fabricate')
    
    move_picking_id = fields.Many2one(comodel_name='stock.move')
    raw_matt_product_id = fields.Many2one(comodel_name='product.product')
    
    @api.depends('sale_line_id', 'fabricate_line_id')
    def _compute_indent_details(self):
        for rec in self:
            rec.contract_ref = ''
            rec.customer = ''
            rec.series_id = 0
            if rec.sale_line_id:
                rec.contract_ref = rec.sale_line_id.order_id.name
                rec.series_id = rec.sale_line_id.series_id
                rec.customer = rec.sale_line_id.order_id.partner_id.name
                
            elif rec.fabricate_line_id:
                customer = rec.env['sale.order'].search([('name','=', rec.fabricate_line_id.raw_material_production_id.origin)], limit=1)
                rec.contract_ref = rec.fabricate_line_id.raw_material_production_id.origin
                rec.series_id = rec.fabricate_line_id.product_id.series_id
                rec.customer = customer.partner_id.name
                rec.date_order = customer.date_order
                rec.name = rec.fabricate_line_id.raw_material_production_id.origin
                
            elif rec.move_picking_id:
                customer = rec.env['sale.order'].search([('name','=', rec.move_picking_id.picking_id.origin)], limit=1)
                if rec.move_picking_id.picking_id.sale_id:
                    rec.contract_ref = rec.move_picking_id.picking_id.sale_id.name
                    rec.series_id = rec.move_picking_id.product_id.series_id
                    rec.customer = rec.move_picking_id.picking_id.sale_id.partner_id.name
                    rec.date_order = rec.move_picking_id.picking_id.sale_id.date_order
                    rec.name = rec.move_picking_id.picking_id.origin
                else:
                    rec.contract_ref = rec.move_picking_id.picking_id.origin
                    rec.series_id = rec.move_picking_id.product_id.series_id
                    rec.customer = customer.partner_id.name
                    rec.date_order = customer.date_order
                    rec.name = rec.move_picking_id.picking_id.origin
        
    @api.depends('product_id')
    def get_product_id(self):
        for rec in self:
            if rec.sale_line_id.to_fabricate:
                for component in rec.sale_line_id.bom.bom_line_ids:
                    rec.product_id = component.product_id
                    
            elif rec.move_picking_id:
                if rec.raw_matt_product_id:
                    rec.product_id = rec.raw_matt_product_id
                else:
                    rec.product_id = rec.move_picking_id.product_id
            else:
                rec.product_id = rec.sale_line_id.product_id if rec.sale_line_id else rec.fabricate_line_id.product_id
                
            