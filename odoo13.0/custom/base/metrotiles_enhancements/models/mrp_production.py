from odoo import models, fields, api

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    sales_person = fields.Many2one('res.users', string="Salesperson", store=True, compute="compute_so_details")
    contract_client = fields.Many2one('res.partner', string="Client", store=True, compute="compute_so_details")

    factory_id = fields.Many2one('res.partner', string='Factory', readonly=False, store=True, compute="get_fact_series" )
    series_id = fields.Many2one('metrotiles.series', string='Series', readonly=False, store=True, compute="get_fact_series")

    variant = fields.Char(string="Variant", compute='get_variant_from_product', store=True, )
    size = fields.Char(string="Sizes (cm)", compute='get_variant_from_product', store=True,)
 
    @api.depends('product_id')
    def get_fact_series(self):
        for record in self:
            factory = None
            series = None
            if record.product_id:
                for products in record.product_id:
                    if products.variant_seller_ids:
                        factory = products.variant_seller_ids[0].name
                    if products:
                        series = products.series_id.id
            record.update({
                'factory_id': factory, 'series_id': series,
            })
            
    @api.depends('product_id')
    def get_variant_from_product(self):
        for rec in self:
            variant = 'N/A'
            size = 'N/A'
            for attr in rec.product_id.product_template_attribute_value_ids:
                if attr.attribute_id.name == 'Variants':
                    variant = attr.name
                elif attr.attribute_id.name == 'Sizes':
                    size = attr.name

            rec.update({'variant': variant, 'size': size})
    
    @api.depends('origin')
    def compute_so_details(self):
        for rec in self:
            sale_id = self.env['sale.order'].search([('name', '=', rec.origin)])
            rec.sales_person = sale_id.user_id.id
            rec.contract_client = sale_id.partner_id.id