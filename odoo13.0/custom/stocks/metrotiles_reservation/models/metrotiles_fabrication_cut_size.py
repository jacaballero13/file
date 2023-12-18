from odoo import models, fields, api, exceptions


class MetrotilesFabricationRawMaterial(models.Model):
    _name = 'metrotiles.fabrication.cut.size'

    name = fields.Char(compute="get_name", store=True)
    sale_order_line_id = fields.Many2one('sale.order.line')

    cut_height = fields.Integer(string="Height", default=0.0)
    cut_width = fields.Integer(string="Width", default=0.0)

    price_unit = fields.Float(string="Price", default=0.0, compute="compute_price_unit")

    quantity = fields.Integer(string="Produce Quantity", default=0)
    total = fields.Float(string="Total", default=0, store=True, compute="compute_total")

    @api.depends('cut_height', 'cut_width')
    def compute_price_unit(self):
        for rec in self:
            product_id = self._context.get('product_tmpl_id')
            variant = self._context.get('variant')
            price_unit = 0.0
            product = self.env['product.product'].search([
                ('product_tmpl_id', '=', product_id),
                ('product_template_attribute_value_ids.name', '=', variant),
                ('product_template_attribute_value_ids.name', '=', "{}x{}".format(rec.cut_width, rec.cut_height))
            ], limit=1)

            if product.id:
                print(product)
                price_unit = product.lst_price

            rec.update({'price_unit': price_unit})

    @api.depends('price_unit', 'quantity')
    def compute_total(self):
        for rec in self:
            rec.update({'total': rec.price_unit * rec.quantity})

    @api.depends('cut_height', 'cut_width')
    def get_name(self):
        for rec in self:
            rec.update({'name': '{}x{}'.format(rec.cut_height, rec.cut_width)})