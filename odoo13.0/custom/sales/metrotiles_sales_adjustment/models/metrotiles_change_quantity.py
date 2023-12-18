# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class MetrotilesChangeQuantity(models.Model):
    _name = 'metrotiles.change.quantity'
    
    
    change_quant_ids =  fields.One2many(
        comodel_name="metrotiles.change.quantity.lines",
        inverse_name="change_quant_id",
        store=True,
        string="Change Quantity"
    )
    sales_order_id = fields.Many2one(
        string="Contract Reference",
        comodel_name="sale.order",
        store=True,
        required=True, 
    )
    adjustment_type = fields.Selection(
        string="Adjustment Type",
        readonly=True,
        selection=[
                ('cancel_contract', 'Cancellation of Contract'), 
                ('cancel_items', 'Cancellation of Items'),
                ('change_designer', 'Change Architect & Interior Designer'),
                ('change_charges', 'Change Contract Charges'),
                ('change_items', 'Change Items'),
                ('change_discount', 'Change Discount'),
                ('change_qty', 'Change Quantity'),
                ('change_vat', 'Change VAT'),
    ])
    # column_discounts = fields.Many2many('metrotiles.discount',
    #             'metrotiles_discount_column_change_quantity_rel',
    #             string="Column discounts")

    @api.onchange('sales_order_id')
    def _onchange_order_line(self):
        lines = []
        for rec in self:
            if rec.sales_order_id: 
                order_line_ids = self.env['sale.order.line'].search([('order_id', '=', rec.sales_order_id.id), ('product_uom_qty', '>', 0)])
                for order in order_line_ids:
                    lines.append((0,0,{
                        'location_id': order.location_id.id,
                        'application_id': order.application_id.id,
                        'factory_id': order.factory_id.id,
                        'series_id': order.series_id.id,
                        'product_id': order.product_id.id,
                        'package_id': order.package_id.id,
                        'size': order['size'],
                        'variant': order['variant'],
                        'price_unit': order.price_unit,
                        'column_discounts': order.discounts,
                        'total_qty': order.product_uom_qty,
                        'rif': order.rif,
                        'qty_delivered': order.qty_delivered,
                        'new_qty': order.product_uom_qty,
                    }))
                rec.update({
                    'change_quant_ids': lines,
                })
    def action_change_quantity(self):
        change_quants_lines = []
        order_id = self.env['sale.order'].search([('id','=', self.sales_order_id.id)])
        orders = order_id.filtered(lambda s: s.state in ['cancel', 'sent'])
        sale_adjustment_ids = self.env['sales.order.adjustment'].search([])
        for rec in self:
            for change_quants in rec.change_quant_ids:
                if len(change_quants) > 0:
                    change_quants_lines.append((0,0,{
                        'location_id': change_quants.location_id.id,
                        'application_id': change_quants.application_id.id,
                        'factory_id': change_quants.factory_id.id,
                        'series_id': change_quants.series_id.id,
                        'product_id': change_quants.product_id.id,
                        'package_id': change_quants.package_id.id,
                        'size': change_quants['size'],
                        'variant': change_quants['variant'],
                        'price_unit': change_quants.price_unit, 
                        'column_discounts': change_quants.column_discounts,
                        'total_qty': change_quants.total_qty,
                        'rif': change_quants.rif,
                        'qty_delivered': change_quants.qty_delivered,
                        'new_qty': change_quants.new_qty,
                    }))
            sale_adjustment_ids.create({
                'change_quantity_lines': change_quants_lines,
                'sale_order_id': rec.sales_order_id.id,
                'adjustment_type': rec.adjustment_type,
            })
        return orders.write({
            'state': 'draft',
            'signature': False,
            'signed_by': False,
            'signed_on': False,
        })
    def action_create_new(self):
        saf_wiz = self.env.ref('metrotiles_sales_adjustment.metrotiles_saf_wizard_view_form')
        for rec in self:
            self.action_change_quantity()
            return {
                    'name': "Sales Adjustmet Page",
                    'view_mode': 'form',
                    'view_id': saf_wiz.id,
                    'view_type': 'form',
                    'res_model': 'metrotiles.saf.wizard',
                    'type': 'ir.actions.act_window',
                    'target': 'new',
                    'context':{
                        'default_sales_order_id': rec.sales_order_id.id,
                    }
                }        

class MetrotilesChangeQuantityLines(models.Model):
    _name ='metrotiles.change.quantity.lines'
    

    change_quant_id = fields.Many2one(comodel_name="metrotiles.change.quantity", string="change quants")
    saf_adjustment_ids = fields.Many2one(
        string='SAF Adjustment',
        comodel_name='sales.order.adjustment',
        store=True,
    )
    
    package_id = fields.Many2one('stock.quant.package', 
        string="Package ID")
    location_id = fields.Many2one(
        comodel_name="metrotiles.location",
        string="Location",
        store=True,
    )
    application_id = fields.Many2one(string='Application',
        comodel_name='metrotiles.application',
        store=True,
    )
    factory_id = fields.Many2one(
        comodel_name="res.partner",
        string="Factory",
        store=True,
    )
    series_id = fields.Many2one(
        comodel_name="metrotiles.series",  
        string="Series",
    )
    price_unit = fields.Float(
        string="Price Unit",
        store=True,
    )
    column_discounts = fields.Many2many('metrotiles.discount',
            'metrotiles_discount_column_change_quantity_lines_rel',
            string="Column discounts")
    product_id = fields.Many2one(
        string='Product',
        comodel_name='product.product',
    )
    size = fields.Char(
        string='Size',
    )
    variant = fields.Char(
        string='Variant',
    )
    total_qty = fields.Float(
        string="Total Qty"
    )
    rif = fields.Char(
        string="R|I|F"
    )
    qty_delivered = fields.Float(
        string="Delivered Qty"
    )
    new_qty = fields.Float(
        string="New Qty"
    )
    
    