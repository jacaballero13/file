from odoo import models, fields, api, exceptions


class MetrotilesFabricationRawMaterial(models.Model):
    _name = 'metrotiles.fabrication.raw.material'

    name = fields.Char()
    stock_quant = fields.Many2one('stock.quant', string="Raw Material", required=True)
    product_id = fields.Many2one('product.product', string="Raw Material", compute="get_product_from_stock_quant",
                                 store=True)

    variant = fields.Char(string="Variant", compute="get_variant_from_product")
    size = fields.Char(string="Sizes (cm)", compute="get_variant_from_product")
    quantity = fields.Float(string="Quantity")

    cut_height = fields.Float(string="Height", default=0.0)
    cut_width = fields.Float(string="Width", default=0.0)
    new_quantity = fields.Integer(string="New Quantity", default=0)

    sale_order_id = fields.Many2one('sale.order')
    sale_order_line_id = fields.Many2one('sale.order.line')

    @api.depends('stock_quant')
    def get_product_from_stock_quant(self):
        for rec in self:
            rec.update({'product_id': rec.stock_quant.product_id})

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

    def update_product_temp_reserved(self, reserved_qty, location_id):
        if reserved_qty > 0:
            product_temp_reserved = self.env['metrotiles.product.temp.reserved'].sudo().search(
                [('stock_location_id', '=', location_id),
                 ('sale_line_id', '=', self.sale_order_line_id.id),
                 ('is_for_fabrication', '=', True),
                 ('product_id', '=', self.product_id.id)
                 ]
            )

            print(['qweqwe',product_temp_reserved])
            if not product_temp_reserved.id:
                product_temp_reserved.create(
                    {
                        'sale_line_id': self.sale_order_line_id.id,
                        'stock_location_id': location_id,
                        'product_id': self.product_id.id,
                        'quantity': reserved_qty,
                        'is_for_fabrication': True
                    })
                print(product_temp_reserved)
            else:
                product_temp_reserved.update({'quantity': reserved_qty})

        else:
            product_temp_reserved = self.env['metrotiles.product.temp.reserved'].sudo().search(
                [('stock_location_id', '=', location_id), ('sale_line_id', '=', self.sale_order_line_id.id),
                 ('is_for_fabrication', '=', True)])

            product_temp_reserved.unlink()

    @api.model
    def create(self, values):
        res = super(MetrotilesFabricationRawMaterial, self).create(values)

        res.stock_quant.sudo().update({'temp_reserved': res.stock_quant.temp_reserved + res.quantity})

        res.update_product_temp_reserved(res.quantity, res.stock_quant.location_id.id)

        return res

    def write(self, values):
        prev_stock_id = None

        if values.get('stock_quant'):
            prev_stock_id = self.stock_quant

        res = super(MetrotilesFabricationRawMaterial, self).create(values)

        if prev_stock_id:
            self.env['metrotiles.product.temp.reserved'].sudo().search(
                [
                    ('stock_location_id', '=', prev_stock_id.location_id.id),
                    ('sale_line_id', '=', self.sale_order_line_id.id),
                    ('product_id', '=', self.product_id.id),
                    ('is_for_fabrication', '=', True),
                 ]
            ).unlink()
            self.update_product_temp_reserved(self.quantity, self.stock_quant.location_id.id)
        elif values.get('quantity'):

            self.stock_quant.sudo().update({'temp_reserved': self.stock_quant.temp_reserved + self.quantity})
            self.update_product_temp_reserved(self.quantity, self.stock_quant.location_id.id)

    #
    # def name_get(self):
    #     print('qwe')
    #     return []


class MetrotilesFabricationRawMaterialCutSize(models.Model):
    _name = 'metrotiles.fabrication.raw.material.cut.size'

    name = fields.Char()
    fab_raw_material_id = fields.Many2one('metrotiles.fabrication.raw.material', string="Raw Material")
    height = fields.Float('height', default=0.0)
    width = fields.Float('width', default=0.0)
    quantity = fields.Integer('quantity', default=0)
