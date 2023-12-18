# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError




class MetrotilesChangeDesignerCommision(models.Model):
    _name = 'metrotiles.changes.designer.commision'
    _description = "Change Designer Comission"
    
    
    architect_page_id = fields.One2many(
        comodel_name='metrotiles.architect.lines', 
        inverse_name='architect_line_id', 
        string="Architect Page", 
        store=True, 
    )
    designer_page_id = fields.One2many(
        string='Interior Desinger Page',
        comodel_name='metrotiles.designer.lines',
        inverse_name='change_designer_id',
        store=True,
    )
    sales_order_id = fields.Many2one(
        string="Contract Reference",
        comodel_name="sale.order",
        store=True,
        readonly=True,
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
    
    def action_change_designer(self):
        architect_lines = []
        designer_lines = []
        order_id = self.env['sale.order'].search([('id','=', self.sales_order_id.id)])
        orders = order_id.filtered(lambda s: s.state in ['cancel', 'sent'])
        sale_adjustment_ids = self.env['sales.order.adjustment'].search([])
        for rec in self:
            for architect in rec.architect_page_id:
                architect_lines.append((0,0,{
                    'architect_id': architect.architect_id.id,
                    'architect_com_type': architect.architect_com_type,
                    'architect_commission': architect.architect_commission,
                    'architect_subtotal_price': architect.architect_subtotal_price,
                    'designer_initial_price_value': order_id.architect_total_price,
                    'architect_adjust_total': architect.architect_adjust_total,
                }))
            for designer in rec.designer_page_id:
                designer_lines.append((0,0,{
                    'designer_id': designer.designer_id.id,
                    'designer_com_type': designer.designer_com_type,
                    'designer_commission': designer.designer_commission,
                    'designer_subtotal_price': designer.designer_subtotal_price,
                    'designer_initial_price_value': order_id.designer_total_price,
                    'designer_adjust_total': designer.designer_adjust_total,
                }))
            sale_adjustment_ids.create({
                'change_architect_lines': architect_lines,
                'change_designer_lines': designer_lines,
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
            self.action_change_designer()
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
            
        # lines = [(5,0,0)]
        # for rec in self:
        #     for architect in rec.architect_page_id:
        #         lines.append((0,0,{
        #             'architect_id': architect.architect_id.id,
        #             'architect_com_type': architect.architect_com_type,
        #             'architect_commission': architect.architect_commission,
        #             'architect_subtotal_price': architect.architect_subtotal_price,
        #         }))
        #         rec.sales_order_id.update({
        #             'architect_ids': lines,
        #         })
        # return lines
        
class MetrotilesArchitectLines(models.Model):
    _name = 'metrotiles.architect.lines'
    _description = "Architect page details"
    
    
    architect_line_id = fields.Many2one(
        string="Designer Commision Page", 
        comodel_name="metrotiles.changes.designer.commision",
        store=True,)
    saf_adjustment_ids = fields.Many2one(
        string='SAF Adjustment',
        comodel_name='sales.order.adjustment',
        store=True,
    )
    sale_order = fields.Many2one(
        string="Sale Order",
        comodel_name="sale.order",
        store=True,
    )
    # Architects page details
    architect_name = fields.Char('Architect Name')
    architect_id = fields.Many2one('res.partner', string="Architect Name", domain=[("category_id.name", "=ilike", "architect")])
    architect_sale_id = fields.Many2one(string='sale', comodel_name='sale.order')
    architect_com_type = fields.Selection(string='Commission type',
                                        selection=[('percentage', 'Percentage'), ('amount', 'Amount')])
    architect_commission = fields.Float(string='Commission')
    designer_initial_price_value = fields.Monetary(
                                string="Initial Price value",
                                currency_field="architect_currency_id", store=True)
    architect_subtotal_price = fields.Monetary(currency_field="architect_currency_id", string="Current Total", store=True, readonly=True)
    architect_adjust_total = fields.Monetary(compute='_get_architect_subtotal_price', currency_field="architect_currency_id", store=True, string="Adjustment Total")
    architect_currency_id = fields.Many2one('res.currency', string='Currency')

    @api.depends('architect_com_type', 'architect_commission', 'designer_initial_price_value')
    def _get_architect_subtotal_price(self):
        for price in self:
            if price.architect_com_type == 'percentage':
                total = ((price.architect_commission or 0.0) / 100) * price.designer_initial_price_value
                price.update({'architect_adjust_total': total})
            else:
                price.architect_adjust_total = price.architect_commission

    # constraint - architect_com_type, architect_commission
    @api.constrains('architect_com_type', 'architect_commission')
    def _validate_architect_commission(self):
        for field in self:
            if field.architect_com_type == 'percentage':
                if (field.architect_commission > 100) or (field.architect_commission <= 0):
                    raise UserError( "Percentage fields must be less than equal to 100 or greater than 0")

class MetrotilesDesignerLines(models.Model):
    _name = 'metrotiles.designer.lines'
    
    change_designer_id = fields.Many2one(string="Designer", comodel_name="metrotiles.changes.designer.commision")
    saf_adjustment_ids = fields.Many2one(
        string='SAF Adjustment',
        comodel_name='sales.order.adjustment',
        store=True,
    )
    
    designer_name = fields.Char('Interior Designer')
    designer_id = fields.Many2one('res.partner', string="Designer Name", domain=[("category_id.name", "=ilike", "Interior Designer")])
    designer_sale_id = fields.Many2one(string='sale', comodel_name='sale.order')
    designer_com_type = fields.Selection(string='Commission type',
                                        selection=[('percentage', 'Percentage'), ('amount', 'Amount')])
    designer_commission = fields.Float(string='Commission')
    designer_currency_id = fields.Many2one('res.currency', string='Currency')
    designer_initial_price_value = fields.Monetary(
                    string="Initial Price value",
                    currency_field="designer_currency_id", store=True)
    designer_subtotal_price = fields.Monetary(currency_field="designer_currency_id", string="Current Total", store=True, readonly=True)
    designer_adjust_total = fields.Monetary(compute='_get_designer_subtotal_price', currency_field="designer_currency_id", string="Subtotal", store=True)
    
    @api.depends('designer_com_type', 'designer_commission', 'designer_initial_price_value')
    def _get_designer_subtotal_price(self):
        for price in self:
            if price.designer_com_type == 'percentage':
                price.designer_adjust_total = ((price.designer_commission or 0.0) / 100) \
                                                * price.designer_initial_price_value
            else:
                price.designer_adjust_total = price.designer_commission
    
    # constraint - designer_com_type, designer_commission
    @api.constrains('designer_com_type', 'designer_commission')
    def _validate_designer_commission(self):
        for field in self:
            if field.designer_com_type == 'percentage':
                if (field.designer_commission > 100) or (field.designer_commission <= 0):
                    raise UserError("Percentage fields must be less than equal to 100 or greater than 0")