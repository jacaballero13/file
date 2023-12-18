# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class MetrotilesChangeVat(models.Model):
    _name = 'metrotiles.change.vat'
    
    
    sales_order_id = fields.Many2one(
        string="Contract Reference",
        comodel_name="sale.order",
        store=True,
        required=True, 
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
    current_vat = fields.Many2one(
        comodel_name="account.tax",
        string="Current Vat Type",
        readonly= True,
        default=lambda self: self.default_tax_id()
    )
    def default_tax_id(self):
        params = self.env['ir.config_parameter'].sudo()
        vat_id = int(params.get_param('vat', default=0))
        vat_enabled = bool(params.get_param('vat_enabled', default=False))

        if vat_enabled and vat_id > 0:
            return self.env['account.tax'].sudo().search([('id', '=', vat_id)])
        else:
            return self.env.company.account_sale_tax_id
    
    
    # new_vat_type = fields.Many2one(
    #     comodel_name="account.tax",
    #     string="Change Vat Type",
    #     store=True,
    # )
    new_vat_type = fields.Selection(
        string='Change Vat Type',
        selection=[('vat', 'VATABLE'), ('novat', 'NON-VATABLE')]
    )
    

    def action_change_vat(self):
        order_id = self.env['sale.order'].search([('id','=', self.sales_order_id.id)])
        orders = order_id.filtered(lambda s: s.state in ['cancel', 'sent'])
        sale_adjustment_ids = self.env['sales.order.adjustment'].search([])
        for rec in self:
            sale_adjustment_ids.create({
                'current_vat': rec.current_vat.id,
                'new_vat_type': rec.new_vat_type,
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
            self.action_change_vat()
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
    
    