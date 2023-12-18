from odoo import models, fields, api, exceptions, _


class MetrotilesSaleIndention(models.Model):
    _name = 'metrotiles.sale.indention'

    name = fields.Char()
    quantity = fields.Integer('Quantity')
    po_qty = fields.Integer('PO Qty')
    po_line_id = fields.One2many('purchase.order.line', 'indention_id', string='Indent Purchase Line', domain=[('order_id.state','not in', ('cancel', 'done'))])
    sale_line_id = fields.Many2one('sale.order.line', string="Sale Order Line", required=True)
    factory_id = fields.Many2one('res.partner', string="Factory", required=True)
    to_purchase_qty = fields.Integer('Purchase Qty', default=0, store=True)

    contract_ref = fields.Char(related='sale_line_id.order_id.name', string="Contract Ref.")
    customer = fields.Char(related='sale_line_id.order_id.partner_id.name', string="Customer")
    product_id = fields.Many2one('product.product', string="Product", compute="get_product_id")
    series_id = fields.Many2one('metrotiles.series', related="sale_line_id.series_id", string='Series')
    to_fabricate = fields.Boolean('to_fabricate')

    balance = fields.Integer(string='Balance', compute='count_balance', store=True)

    @api.constrains('to_purchase_qty')
    def check_purchase_qty(self):
        if self.balance - self.to_purchase_qty < 0:
            pass
            # raise exceptions.UserError(
            #     _('Cannot set quantity that is greater than contract Indent Balance'))

    @api.depends('product_id')
    def get_product_id(self):
        for rec in self:
            if rec.sale_line_id.to_fabricate:
                for component in rec.sale_line_id.bom.bom_line_ids:
                    rec.product_id = component.product_id
            else:
                rec.product_id = rec.sale_line_id.product_id

            if rec.sale_line_id.id in (658599,658602,658605):
                rec.product_id = 77326

    @api.depends('po_line_id')
    def count_balance(self):
        for rec in self:
            count = 0

            for line in rec.po_line_id:
                count += line.product_qty

            rec.update({'balance': rec.quantity - count, 'po_qty': count})

    def create(self, values):
        if values.get('quantity', False):
            values['balance'] = values.get('quantity')

        res = super(MetrotilesSaleIndention, self).create(values)

        res.name = res.sale_line_id.order_id.name

        return res

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

    #     res = super(MetrotilesSaleIndention, self).unlink()

    #     for temp_reserved in to_deletes:

    #         stock = self.env['stock.quant'].sudo().search(
    #             [('location_id', '=', temp_reserved.get('location_id')), ('product_id', '=', temp_reserved.get('product_id'))])

    #         if stock.id:
    #             stock.update({'temp_reserved': stock.temp_reserved - temp_reserved.get('quantity')})

    #     return res
