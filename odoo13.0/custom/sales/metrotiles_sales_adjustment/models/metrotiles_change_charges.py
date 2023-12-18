# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError



class MetrotilesChangeCharges(models.Model):
    _name = 'metrotiles.changes.charges'
    _description = "Changing Cutting Chages"


    charge_ids = fields.One2many(
        string='Change Charges',
        comodel_name='metrotiles.change.charges',
        inverse_name='charge_line_id',
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
    
    @api.onchange('sales_order_id')
    def _onchange_charge_lines(self):
        lines = []
        for rec in self:
            if rec.sales_order_id:
                sales_order = self.env['metrotiles.charges'].search([('charge_sale_id','=', self.sales_order_id.id)])
                for charge in sales_order:
                    lines.append((0,0,{
                        'charge_id': charge.charge_id.id,
                        'charge_amount': charge.charge_amount,
                    }))
                rec.update({'charge_ids': lines })
                
    def action_change_charges(self):
        charge_lines = []
        order_id = self.env['sale.order'].search([('id','=', self.sales_order_id.id)])
        orders = order_id.filtered(lambda s: s.state in ['cancel', 'sent'])
        sale_adjustment_ids = self.env['sales.order.adjustment'].search([])
        for rec in self:
            for charge in rec.charge_ids:
                if len(rec.charge_ids) > 0:
                    charge_lines.append((0,0,{
                        'charge_id': charge.charge_id.id,
                        'charge_amount': charge.charge_amount,
                        'charge_adjustment': charge.charge_adjustment,
                    }))
            sale_adjustment_ids.create({
                'change_charges_lines': charge_lines,
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
            self.action_change_charges()
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
            
class MetrotilesChangeCharges(models.Model):
    _name = 'metrotiles.change.charges'
    
    charge_line_id = fields.Many2one(
        comodel_name="metrotiles.changes.charges", 
        string="Charges and Fees", 
        store=True
    )
    saf_adjustment_ids = fields.Many2one(
        string='SAF Adjustment',
        comodel_name='sales.order.adjustment',
        store=True,
    )

    charge_sale_id = fields.Many2one(comodel_name='sale.order', string="Sale Order")
    charge_amount = fields.Float(string="Current", store=True,)

    charge_id = fields.Many2one(
        comodel_name="metrotiles.name_charges",
        string="Charge name",
    )
    charge_name = fields.Char(string="Charge Name")
    charge_adjustment = fields.Float(string="Adjustment")
