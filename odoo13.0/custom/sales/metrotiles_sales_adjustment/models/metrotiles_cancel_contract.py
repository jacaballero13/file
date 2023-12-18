# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class MetrotilesCancelContract(models.Model):
    _name = 'metrotiles.cancel.contract'
    _description = "Cancellation of Contract"
    
    
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
    
    def action_cancel_contract(self):
        sale_adjustment_ids = self.env['sales.order.adjustment'].search([])
        order_id = self.env['sale.order'].search([('id','=', self.sales_order_id.id)])
        orders = order_id.filtered(lambda s: s.state in ['cancel', 'sent'])
        pull_outs_obj = self.env['metrotiles.pull.outs']
        for rec in self:
            if rec.sales_order_id:
                sale_adjustment_ids.create({
                    'sale_order_id': rec.sales_order_id.id,
                    'adjustment_type': rec.adjustment_type,
                })
                
                # pull_outs_obj.create({
                #     'sale_order_id': rec.sale_order_id.id,
                #     'partner_id': rec.partner_id.id,
                #     'pullout_type': 'saf', 
                #     'pu_order_lines': change_quants_lines,
                # })

            return orders.write({
                'state': 'draft',
                'signature': False,
                'signed_by': False,
                'signed_on': False,
            })
            
            

    def action_create_new(self):
        saf_wiz = self.env.ref('metrotiles_sales_adjustment.metrotiles_saf_wizard_view_form')
        for rec in self:
            self.action_cancel_contract()
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