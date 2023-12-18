# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class MetrotilesChangeItem(models.Model):
    _name = 'metrotiles.change.item'
    
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
                        'size': order['size'],
                        'variant': order['variant'],
                        'price_unit': order.price_unit,
                        'column_discounts': order.discounts,
                        'total_qty': order.product_uom_qty,
                        'rif': order.rif,
                        'qty_delivered': order.qty_delivered,
                    }))
                rec.update({
                    'change_item_ids': lines
                })

    change_item_ids = fields.One2many(
        comodel_name="metrotiles.change.item.lines",
        inverse_name="change_item_id",
        string="Change Items",
        store=True,
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
    
    
    
    def action_change_items(self):
        change_item_lines = []
        order_id = self.env['sale.order'].search([('id','=', self.sales_order_id.id)])
        orders = order_id.filtered(lambda s: s.state in ['cancel', 'sent'])
        sale_adjustment_ids = self.env['sales.order.adjustment'].search([]) 
        for rec in self:
            for change_items in rec.change_item_ids:
                if len(change_items) > 0:
                    change_item_lines.append((0,0,{
                        'location_id': change_items.location_id.id,
                        'application_id': change_items.application_id.id,
                        'factory_id': change_items.factory_id.id,
                        'series_id': change_items.series_id.id,
                        'product_id': change_items.product_id.id,
                        'package_id': change_items.package_id.id,
                        'size': change_items['size'],
                        'variant': change_items['variant'],
                        'price_unit': change_items.price_unit,
                        'column_discounts': change_items.column_discounts,
                        'total_qty': change_items.total_qty,
                        'rif': change_items.rif,
                        'qty_delivered': change_items.qty_delivered,
                    }))
            sale_adjustment_ids.create({
                'change_item_lines': change_item_lines,
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
            self.action_change_items()
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


class MetrotilesChangeItemLines(models.Model):
    _name = 'metrotiles.change.item.lines'
    
    change_item_id = fields.Many2one(comodel_name="metrotiles.change.item" ,string="Change Item")     
    saf_adjustment_ids = fields.Many2one(
        string='SAF Adjustment',
        comodel_name='sales.order.adjustment',
        store=True,
    )
    select = fields.Boolean('Select')
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
    product_id = fields.Many2one(
        string='Product',
        comodel_name='product.product',
        store=True,
    )
    size = fields.Char(
        string='Size',
        store=True,
    )
    variant = fields.Char(
        string='Variant',
        store=True,
    )
    price_unit = fields.Float(
        string="Price Unit",
        store=True,
    )
    column_discounts = fields.Many2many('metrotiles.discount',
            'metrotiles_discount_column_change_item_lines_rel',
            string="Column discounts")
    rif = fields.Char(
        string="R|I|F",
        store=True,
    )
    total_qty = fields.Float(
        string="Total Qty",
        store=True,
    )
    qty_delivered = fields.Float(
        string="Delivered Qty",
        store=True,
    )

    @api.onchange('product_id')
    def _onchange_change_products(self):
        for rec in self:
            variant = 'N/A'
            size = 'N/A'

            for attr in rec.product_id.product_template_attribute_value_ids:
                if attr.attribute_id.name == 'Variants':
                    variant = attr.name
                elif attr.attribute_id.name == 'Sizes':
                    size = attr.name

            rec.update({'variant': variant, 'size': size})