# Metrotiles Quotation Template
#
# This model will inherit sale order template and reconstruct sale quotation preview to include new fields in the report.
from odoo import models, api, fields


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.template.line'

    location_id = fields.Many2one('metrotiles.location', string="Location", store=True)
    application_id = fields.Many2one('metrotiles.application', string="Application", store=True)
    price_unit = fields.Float('Gross Price', required=True, digits='Product Price', default=0.0)
    price_net = fields.Float(compute='get_net_price', string="Net Price", readonly=True)

    factory_id = fields.Many2one('res.partner', string='Factory', store=True, )
    series_id = fields.Many2one('metrotiles.series', string='Series', readonly=False, store=True)

    name = fields.Text(string='Description', required=False)

    @api.onchange('factory_id')
    def factory_onchange(self):
        for field in self:
            field.series_id = None
            return {'domain': {"series_id": [("partners_ids", "=", field.factory_id.id)]}}

    @api.onchange('series_id')
    def series_onchange(self):
        for field in self:
            if field.series_id.id != field.product_id.series_id.id:
                field.product_id = None
            return {'domain': {"product_id": ['&', ("series_id", "=", field.series_id.id), ('sale_ok', '=', True)]}}

    @api.depends('product_id')
    def get_net_price(self):
        total_net = 0.0
        for line in self:
            total_net = line.price_unit * (1 - line.discount / 100)
            line.update({
                'price_net': total_net,
            })

    @api.onchange('product_id')
    def product_change(self):
        if self.product_id.product_tmpl_id.type == 'installation':
            application_exist = self.env['metrotiles.application'].search(
                [('name', 'ilike', self.product_id.product_tmpl_id.name)], limit=1)
            if application_exist.name:
                self.application_id = application_exist
            else:
                self.application_id = self.env['metrotiles.application'].create(
                    {'name': self.product_id.product_tmpl_id.name})
