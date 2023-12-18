# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError



class MetrotilesCancelItem(models.Model):
    _name = 'metrotiles.cancel.item'
    _description = "Cancellation of Items in Order Lines"
    
    cancel_item_ids = fields.One2many(
        comodel_name="metrotiles.cancel.item.lines",
        inverse_name="cancel_item_id",
        store=True,
    )
    sales_order_id = fields.Many2one(
        string="Contract Reference",
        comodel_name="sale.order",
        store=True,
        readonly=True,
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
    
    @api.onchange('sales_order_id')
    def _onchange_change_items(self):
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
                        'price_unit': order.price_unit,
                        'column_discounts': order.discounts,
                        'size': order['size'],
                        'variant': order['variant'],
                        'total_qty': order.product_uom_qty,
                        'rif': order.rif,
                        'qty_delivered': order.qty_delivered,
                    }))
                rec.update({
                    'cancel_item_ids': lines
                })
                
    def action_cancel_items(self):
        cancel_item_lines = []
        order_id = self.env['sale.order'].search([('id','=', self.sales_order_id.id)])
        orders = order_id.filtered(lambda s: s.state in ['cancel', 'sent'])
        sale_adjustment_ids = self.env['sales.order.adjustment'].search([]) 
        for rec in self:
            for cancel_items in rec.cancel_item_ids:
                if  len(cancel_items) > 0 :
                    cancel_item_lines.append((0,0,{
                        'select': cancel_items.select,
                        'location_id': cancel_items.location_id.id,
                        'application_id': cancel_items.application_id.id,
                        'factory_id': cancel_items.factory_id.id,
                        'series_id': cancel_items.series_id.id,
                        'price_unit': cancel_items.price_unit,
                        'column_discounts': cancel_items.column_discounts,
                        'product_id': cancel_items.product_id.id,
                        'package_id': cancel_items.package_id.id,
                        'size': cancel_items['size'],
                        'variant': cancel_items['variant'],
                        'total_qty': cancel_items.total_qty,
                        'rif': cancel_items.rif,
                        'qty_delivered': cancel_items.qty_delivered,
                    }))
            sale_adjustment_ids.create({
                'cancel_item_lines': cancel_item_lines,
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
            self.action_cancel_items()
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

    
    
    

class MetrotilesCancelItemLines(models.Model):
    _name = 'metrotiles.cancel.item.lines'
    

    cancel_item_id = fields.Many2one(string="Change Item", comodel_name="metrotiles.cancel.item")     
    
    saf_adjustment_ids = fields.Many2one(
        string='SAF Adjustment',
        comodel_name='sales.order.adjustment',
        store=True,
    )
    select = fields.Boolean(
        string='Cancel',
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
            'metrotiles_discount_column_cancel_item_lines_rel',
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
    
    
