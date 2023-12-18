from odoo import models, fields, api, _
from odoo.exceptions import UserError
import re

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order.line'
    
    price_type = fields.Selection(selection=[('per_piece', 'Piece'),
                                        ('per_sqm', 'SQM')], string='Price Type',default='per_piece')
    
    qty_sqm = fields.Float(string='Qty in SQM')
    order_date = fields.Datetime(string="Order Date", compute="get_so_order_date")
    delivery_address = fields.Char(string="Delivery Address", compute="get_so_order_date")

    @api.depends('indention_id')
    def get_so_order_date(self):
        for rec in self:
            sale_order = self.env['sale.order'].search([('name','=', rec.indention_id.contract_ref)])
            rec.order_date = sale_order.date_order if sale_order else ""
            rec.delivery_address = sale_order.delivery_address if sale_order else ""
    # @api.onchange('price_type')
    # def get_price_type(self):
    #     self.qty_sqm = 0
    #     for rec in self:
    #         if rec.price_type == 'per_sqm':
    #             sizes = []
    #             size = self.size
    #             size_list = re.findall(r"[-+]?\d*\.\d+|\d+",size)
    #             for size in size_list:
    #                 sizes.append(float(size))
                
    #             size = (sizes[0]/100)*(sizes[1]/100)
    #             rec.qty_sqm = size*rec.product_qty
                
    #             subtotal = rec.qty_sqm * rec.price_unit
                
    #             rec.update({'price_subtotal': subtotal})
    #             # rec.price_subtotal = subtotal
            
    #         else:
    #             rec.price_subtotal = rec.product_qty * rec.price_unit
                
    @api.onchange('price_type')
    @api.depends('product_qty', 'price_unit', 'taxes_id','qty_sqm','price_type')
    def _compute_amount(self):
        for line in self:
            vals = line._prepare_compute_all_values()
            taxes = line.taxes_id.compute_all(
                vals['price_unit'],
                vals['currency_id'],
                vals['product_qty'],
                vals['product'],
                vals['partner'])
            if line.price_type == 'per_sqm':
                sizes = []
                size = str(line.size)
                size_list = re.findall(r"[-+]?\d*\.\d+|\d+",size)
                for size in size_list:
                    sizes.append(float(size))
                
                size = (sizes[0]/100)*(sizes[1]/100)
                line.qty_sqm = size*line.product_qty
                
                subtotal = line.qty_sqm * line.price_unit
            else:
                subtotal = taxes['total_excluded']
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': subtotal,
            })
                
                
    