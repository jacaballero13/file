from odoo import models, fields, api

class Installation(models.Model):
    _name = "metrotiles.installation"

    product_id = fields.Many2one("product.product", string='Installation', domain=[('product_tmpl_id.type','=','installation')], required=True)
    gross_price = fields.Monetary(string='Gross Price', default=0.0)
    net_price = fields.Monetary(string='Net Price', default=0.0, compute='get_net_price')
    uom_qty = fields.Float(string='UOM Qty', default=1.0)
    uom = fields.Many2one('uom.uom', string='Unit of Measure')
    subtotal = fields.Monetary(string='Subtotal', default=0.0, compute="compute_subtotal")
    order_id = fields.Many2one('sale.order', string="Order Id")

    salesman_id = fields.Many2one(related='order_id.user_id', store=True, string='Salesperson', readonly=True)
    currency_id = fields.Many2one(related='order_id.currency_id', depends=['order_id.currency_id'], store=True,
                                  string='Currency', readonly=True)
    company_id = fields.Many2one(related='order_id.company_id', string='Company', store=True, readonly=True, index=True)
    order_partner_id = fields.Many2one(related='order_id.partner_id', store=True, string='Customer', readonly=False)

    @api.depends('gross_price')
    def get_net_price(self):
        for rec in self:
            rec.update({'net_price': rec.gross_price})

    @api.depends('net_price', 'uom_qty')
    def compute_subtotal(self):
        for rec in self:
            rec.update({'subtotal': rec.net_price * rec.uom_qty})

    @api.onchange('product_id')
    def _check_change(self):
        if self.product_id:
            self.update({'gross_price': self.product_id.list_price, 'uom': self.product_id.uom_id})

