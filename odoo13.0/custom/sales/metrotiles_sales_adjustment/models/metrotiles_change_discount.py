# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class MetrotilesChangeDiscount(models.Model):
    _name = 'metrotiles.change.discount'
    
    
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
    
    column_discounts = fields.Many2many('metrotiles.discount',
                'metrotiles_discount_column_change_discount_rel',
                string="Column discounts",
                domain="([('discount_type','=','percentage')])",
                store=True,
    )
    total_discounts = fields.Many2many('metrotiles.discount',
                'metrotiles_discount_column_metrotiles_change_discount_rel',
                string="Discounts")
    amount_discount = fields.Float(string='Total Vertical Discount')

    def action_change_discount(self):
        order_id = self.env['sale.order'].search([('id','=', self.sales_order_id.id)])
        orders = order_id.filtered(lambda s: s.state in ['cancel', 'sent'])
        for rec in self:
            sale_adjustment_ids = self.env['sales.order.adjustment']
            if rec.sales_order_id:
                sale_adjustment_ids.create({
                    'sale_order_id': rec.sales_order_id.id,
                    'adjustment_type': rec.adjustment_type,
                    'column_discounts': rec.column_discounts or [(5,0,0)], 
                    'total_discounts': rec.total_discounts or [(5,0,0)]
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
            self.action_change_discount()
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
