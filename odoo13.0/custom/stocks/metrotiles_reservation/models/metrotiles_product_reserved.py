from odoo import models, fields, api, exceptions

class MetrotilesProductReserved(models.Model):
    _name = 'metrotiles.product.reserved'

    name = fields.Char()
    stock_location_id = fields.Many2one('stock.location', string="Stock Location")
    package_id = fields.Many2one('stock.quant.package', string="Pallet Stock")
    
    quantity = fields.Integer('Quantity')
    sale_line_id = fields.Many2one('sale.order.line', string="Sale Order Line", required=True)
    product_id = fields.Many2one('product.product', string="Product")

    order_name = fields.Char(related='sale_line_id.order_id.name', string="Order name")
    client_name = fields.Many2one(related='sale_line_id.order_id.partner_id', string="Client name")
    account_executive = fields.Many2one(related='sale_line_id.order_id.user_id', string="AE")

    def create(self, values):
        res = super(MetrotilesProductReserved, self).create(values)

        res.update({'name': res.sale_line_id.order_id.name})

    # def unlink(self):
    #     """
    #         After deleted free up temporary reserved quantity
    #     """

    #     to_deletes = []
    #     product_ids = []

    #     for temp_reserved in self:
    #         to_deletes.append({
    #             'location_id': temp_reserved.stock_location_id.id,
    #             'product_id': temp_reserved.sale_line_id.product_id.id,
    #             'quantity': temp_reserved.quantity,
    #         })

    #         product_ids.append(temp_reserved.sale_line_id.product_id.id)

    #     res = super(MetrotilesProductReserved, self).unlink()

    #     for temp_reserved in to_deletes:

    #         stock = self.env['stock.quant'].sudo().search(
    #             [('location_id', '=', temp_reserved.get('location_id')), ('product_id', '=', temp_reserved.get('product_id'))])

    #         if stock.id:
    #             stock.update({'temp_reserved': stock.temp_reserved - temp_reserved.get('quantity')})

    #     return res