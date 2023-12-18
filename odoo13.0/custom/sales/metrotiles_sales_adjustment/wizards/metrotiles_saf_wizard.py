# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError



class MetrotilesSafWizard(models.TransientModel):
    _name = 'metrotiles.saf.wizard'
    
    adjustment_type = fields.Selection(
        string="Adjustment Type",
        selection=[
                ('cancel_contract', 'Cancellation of Contract'), 
                ('cancel_items', 'Cancellation of Items'),
                ('change_items', 'Change Items'),
                ('change_qty', 'Change Quantity'),
                ('change_designer', 'Change Architect & Interior Designer'),
                ('change_charges', 'Change Contract Charges'),
                ('change_discount', 'Change Discount'),
                ('change_vat', 'Change VAT'),
    ])
    sales_order_id = fields.Many2one(
        string="Contract Reference",
        comodel_name="sale.order",
        store=True,
        readonly=True,
        required=True, 
        domain=[('state', '=', 'sale')]
    )

    def confirm_saf(self):
        for record in self:
            if record.adjustment_type ==  'cancel_contract':
                if self.sales_order_id.state not in 'sale':
                    raise UserError('Sorry! Creation of SAF is not allowed when contract is not yet Approved by Manager/Admin')
                else:
                    view_wiz = self.env.ref('metrotiles_sales_adjustment.metrotiles_cancel_contract_view_form')
                    return {
                        'name': "Cancel Contract/Sales Order Page",
                        'view_mode': 'form',
                        'view_id': view_wiz.id,
                        'view_type': 'form',
                        'res_model': 'metrotiles.cancel.contract',
                        'type': 'ir.actions.act_window',
                        'target': 'new',
                        'context': {
                            'default_sales_order_id': record.sales_order_id.id,
                            'default_adjustment_type': record.adjustment_type 
                        }
                    }   
            elif record.adjustment_type == 'cancel_items':
                if self.sales_order_id.state not in 'sale':
                    raise UserError('Sorry! Creation of SAF is not allowed when contract is not yet Approved by Manager/Admin')
                else:
                    view_wiz1 = self.env.ref('metrotiles_sales_adjustment.metrotiles_cancel_item_view_form')
                    return {
                        'name': "Cancel Contract Items Page",
                        'view_mode': 'form',
                        'view_id': view_wiz1.id,
                        'view_type': 'form',
                        'res_model': 'metrotiles.cancel.item',
                        'type': 'ir.actions.act_window',
                        'target': 'new',
                        'context': {
                            'default_adjustment_type': record.adjustment_type,
                            'default_sales_order_id': record.sales_order_id.id,
                        }
                    }
            elif record.adjustment_type == 'change_designer':
                if self.sales_order_id.state not in 'sale':
                    raise UserError('Sorry! Creation of SAF is not allowed when contract is not yet Approved by Manager/Admin')
                else:
                    architect_lines = []
                    designer_lines = []
                    change_arhitect_id = self.env['metrotiles.changes.designer.commision'].search([])
                    view_wiz2 = self.env.ref('metrotiles_sales_adjustment.metrotiles_change_designer_commision_view_form')
                    for sale in record.sales_order_id:
                        architect_ids = self.env['metrotiles.architect'].search([('architect_sale_id', '=', self.sales_order_id.id)])
                        for architect in architect_ids:
                            if len(sale.architect_ids) > 0:
                                architect_lines.append((0,0,{
                                    'architect_sale_id': sale.id,
                                    'architect_id': architect.architect_id.id,
                                    'architect_com_type': architect.architect_com_type,
                                    'architect_commission':architect.architect_commission,
                                    'architect_subtotal_price': architect.architect_subtotal_price,
                                    'designer_initial_price_value': sale.architect_total_price,
                                }))
                        designer_ids = self.env['metrotiles.designer'].search([('designer_sale_id', '=', self.sales_order_id.id)])
                        for designer in designer_ids:
                            if len(sale.designer_ids) > 0:
                                designer_lines.append((0,0,{
                                    'designer_sale_id': sale.id,
                                    'designer_id': designer.designer_id.id,
                                    'designer_com_type': designer.designer_com_type,
                                    'designer_commission': designer.designer_commission,
                                    'designer_subtotal_price': designer.designer_subtotal_price,
                                    'designer_initial_price_value': sale.designer_total_price,
                                }))
                            return {
                                'name': "Change Architect/Interior Designer Page",
                                'view_mode': 'form',
                                'view_id': view_wiz2.id,
                                'view_type': 'form',
                                'res_model': 'metrotiles.changes.designer.commision',
                                'type': 'ir.actions.act_window',
                                'target': 'new',
                                'context':{
                                    'default_architect_page_id': architect_lines,
                                    'default_designer_page_id': designer_lines,
                                    'default_adjustment_type': record.adjustment_type,
                                    'default_sales_order_id': record.sales_order_id.id,
                                }
                            }
            elif record.adjustment_type == 'change_items':
                if self.sales_order_id.state not in 'sale':
                    raise UserError('Sorry! Creation of SAF is not allowed when contract is not yet Approved by Manager/Admin')
                else:
                    view_wiz3 = self.env.ref('metrotiles_sales_adjustment.metrotiles_change_item_view_form')
                    return {
                        'name': "Change Item Page",
                        'view_mode': 'form',
                        'view_id': view_wiz3.id,
                        'view_type': 'form',
                        'res_model': 'metrotiles.change.item',
                        'type': 'ir.actions.act_window',
                        'target': 'new',
                        'context': {
                            'default_adjustment_type': record.adjustment_type,
                            'default_sales_order_id': record.sales_order_id.id,
                        }
                }    
            elif record.adjustment_type == 'change_charges':
                if self.sales_order_id.state not in 'sale':
                    raise UserError('Sorry! Creation of SAF is not allowed when contract is not yet Approved by Manager/Admin')
                else:
                    view_wiz4 = self.env.ref('metrotiles_sales_adjustment.metrotiles_changes_charges_view_form')
                    return {
                        'name': "Change Charge Page",
                        'view_mode': 'form',
                        'view_id': view_wiz4.id,
                        'view_type': 'form',
                        'res_model': 'metrotiles.changes.charges',
                        'type': 'ir.actions.act_window',
                        'target': 'new',
                        'context': {
                            'default_adjustment_type': record.adjustment_type,
                            'default_sales_order_id': record.sales_order_id.id,
                        }
                    }  
            elif record.adjustment_type == 'change_discount':
                if self.sales_order_id.state not in 'sale':
                    raise UserError('Sorry! Creation of SAF is not allowed when contract is not yet Approved by Manager/Admin')
                else:
                    view_wiz5 = self.env.ref('metrotiles_sales_adjustment.metrotiles_change_discount_view_form')
                    if view_wiz5:
                        return {
                            'name': "Change Discount Page",
                            'view_mode': 'form',
                            'view_id': view_wiz5.id,
                            'view_type': 'form',
                            'res_model': 'metrotiles.change.discount',
                            'type': 'ir.actions.act_window',
                            'target': 'new',
                            'context': {
                                'default_adjustment_type': record.adjustment_type,
                                'default_sales_order_id': record.sales_order_id.id,
                                'default_column_discounts': [rec.id for rec in record.sales_order_id.column_discounts],
                                'default_total_discounts': [rec.id for rec in record.sales_order_id.total_discounts],    
                            }
                        }  
            elif record.adjustment_type == 'change_qty': 
                if self.sales_order_id.state not in 'sale':
                    raise UserError('Sorry! Creation of SAF is not allowed when contract is not yet Approved by Manager/Admin')
                else: 
                    view_wiz6 = self.env.ref('metrotiles_sales_adjustment.metrotiles_change_quantity_view_form')
                    return {
                        'name': "Change Quantity Page",
                        'view_mode': 'form',
                        'view_id': view_wiz6.id,
                        'view_type': 'form',
                        'res_model': 'metrotiles.change.quantity',
                        'type': 'ir.actions.act_window',
                        'target': 'new',
                        'context': {
                            'default_adjustment_type': record.adjustment_type,
                            'default_sales_order_id': record.sales_order_id.id,
                        }
                    }  
            elif record.adjustment_type == 'change_vat':
                if self.sales_order_id.state not in 'sale':
                    raise UserError('Sorry! Creation of SAF is not allowed when contract is not yet Approved by Manager/Admin')
                else:
                    view_wiz7 = self.env.ref('metrotiles_sales_adjustment.metrotiles_change_vat_view_form')
                    return {
                        'name': "Change VAT Page",
                        'view_mode': 'form',
                        'view_id': view_wiz7.id,
                        'view_type': 'form',
                        'res_model': 'metrotiles.change.vat',
                        'type': 'ir.actions.act_window',
                        'target': 'new',
                        'context': {
                            'default_adjustment_type': record.adjustment_type,
                            'default_sales_order_id': record.sales_order_id.id,
                        }
                    }  
            else:
                raise UserError('No Adjustment Type Selected !.')
            