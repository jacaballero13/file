# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError



_STATES = [
    ('draft', 'Draft'),
    ('to_approve', 'To be approved'),
    ('second_approve','Approved'),
    ('third_approve','Approved'),
    ('fourth_approve','Approved'),
    ('approved', 'Done'),
    ('rejected', 'Rejected'),
    ('done', 'Done')
]

_STATUS = [
    ('active', 'Active'),
    ('approve_sales', 'Approved by Sales'),
    ('approve_procurment', 'Approved by Procurement'),
    ('approve_accountant', 'Approved by Accountant'),
    ('approve_admin', 'Approved by Admin'),
    ('rejected', "Rejected"),
]
class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    remarks = fields.Selection([
            ('cancel_contract', 'Cancelled'),
        ], string='Remarks')

class SalesOrderAdjustment(models.Model):
    _name = 'sales.order.adjustment'
    _order = 'name desc'
    
    
    
    def button_draft(self):
        self.state = 'draft'
        self.update({'status': 'active'})
    def button_rejected(self):
        self.state = 'rejected'
        self.update({'status': 'rejected'})
    def button_to_approve(self):
        self.state = 'to_approve'
    def button_approve1(self):
        for rec in self:
            if rec.adjustment_type == 'change_discount' or rec.adjustment_type == 'change_designer' or \
                rec.adjustment_type == 'change_discount' or rec.adjustment_type == 'change_vat' or rec.adjustment_type == 'change_charges' or rec.adjustment_type == 'change_quantity': 
                rec.state = 'third_approve'
            # elif rec.adjustment_type == 'cancel_contract':
            #     rec.state = 'fourth_approve' 
            else:
                if rec.adjustment_type == 'cancel_items' or rec.adjustment_type == 'change_items' or \
                    rec.adjustment_type == 'change_qty' or rec.adjustment_type == 'change_charges' or rec.adjustment_type == 'cancel_contract': 
                    rec.state = 'second_approve'
            return rec.update({'status': 'approve_sales'})
    def button_approve2(self):
        for rec in self:
            if rec.adjustment_type == 'cancel_items' or rec.adjustment_type == 'change_items' or \
                rec.adjustment_type == 'change_qty' or rec.adjustment_type == 'cancel_contract': 
                rec.state = 'third_approve'
                # rec.state = 'fourth_approve'
                rec.update({'status': 'approve_procurment' })
            # else:
            #     rec.state = 'third_approve'
    def button_approve3(self):
        self.state = 'fourth_approve'
        self.write({'status': 'approve_accountant'  })
    def button_approved4(self):
        pu_obj = self.env['metrotiles.pull.outs']
        for rec in self:
            reserved_prod = self.env['metrotiles.product.reserved'].search([('order_name','=',rec.sale_order_id.name)])
            spicking = self.env['stock.picking'].search([('origin','=',rec.sale_order_id.name)])
            indent_ids = self.env['metrotiles.sale.indention'].search([('name', '=', rec.sale_order_id.name )])
            if rec.adjustment_type == 'cancel_contract':
                rec.state = 'approved'
                # for warehouse in rec.sale_order_id.warehouse_id:
                #     picking_ids = self.env['stock.picking'].search([('origin','=',rec.sale_order_id.name), ('state', '=', 'done'), ('picking_type_id', '=', warehouse.out_type_id.id)])
                #     if picking_ids:
                #         pu_obj.create({
                #             'sale_order_id': rec.sale_order_id.id,
                #             'partner_id': rec.partner_id.id,
                #             'pullout_type': 'cancel', 
                #         })
                #         for sale in rec.sale_order_id:
                #             sale.write({
                #                 'state': 'done',
                #                 'is_checked': True,
                #                 'is_check_refused': True,
                #                 'check_refused_reason': "Cancelled Contract",
                #             })
                #             rec.state = 'approved'
                #     else:
                #         rec.sale_order_id.action_cancel()
                #         for indent in indent_ids:
                #             if indent:
                #                 indent.unlink()
                #         for prod in reserved_prod:
                #             prod.unlink()
                #         for sale in rec.sale_order_id:
                #             sale.write({
                #                 'state': 'cancel',
                #                 'is_checked': True,
                #                 'is_check_refused': True,
                #                 'check_refused_reason': "Cancelled Contract",
                #             })
            elif rec.adjustment_type == 'cancel_items':
                # cancel_item_lines = [(5,0,0,)]
                # for cancel_items in rec.cancel_item_lines:
                #     rec.sale_order_id.action_cancel()
                #     for pick in spicking:
                #         pick.action_cancel()
                #     for prod in reserved_prod:
                #         prod.unlink()
                #     for indent in indent_ids:
                #         if indent:
                #             indent.unlink()
                #     if not cancel_items.select and len(cancel_items) > 0:
                #         cancel_item_lines.append((0,0,{
                #             'location_id': cancel_items.location_id.id,
                #             'application_id': cancel_items.application_id.id,
                #             'factory_id': cancel_items.factory_id.id,
                #             'series_id': cancel_items.series_id.id,
                #             'product_id': cancel_items.product_id.id,
                #             'package_id': cancel_items.package_id.id,
                #             'size': cancel_items.size,
                #             'variant': cancel_items.variant,
                #             'price_unit': cancel_items.price_unit,
                #             'discounts': cancel_items.column_discounts or ([5,0,0]),
                #             'product_uom_qty': cancel_items.total_qty,
                #             'qty_delivered': cancel_items.qty_delivered,
                #         }))
                #     for sale in rec.sale_order_id:
                #         sale.write({'state': 'draft'})
                #     rec.sale_order_id.update({
                #         'order_line': cancel_item_lines,
                #     })
                rec.state = 'approved'
                    # return method to auto confirm contract order
                    # rec.sale_order_id.action_confirm()
            elif rec.adjustment_type == 'change_designer':
                # architect_lines = [(5,0,0)]
                # designer_lines = [(5,0,0)]
                # for architect in rec.change_architect_lines:
                #     architect_lines.append((0,0,{
                #         'architect_id': architect.architect_id.id,
                #         'architect_com_type': architect.architect_com_type,
                #         'architect_commission': architect.architect_commission,
                #         'architect_subtotal_price': architect.architect_adjust_total,
                #     }))
                # for designer in rec.change_designer_lines:
                #     designer_lines.append((0,0,{
                #         'designer_id': designer.designer_id.id,
                #         'designer_com_type': designer.designer_com_type,
                #         'designer_commission': designer.designer_commission,
                #         'designer_subtotal_price': designer.designer_adjust_total,
                #     }))
                # rec.sale_order_id.update({
                #     'architect_ids': architect_lines,
                #     'designer_ids': designer_lines,
                # })
                rec.state = 'approved'
                # return method to auto confirm contract order
                # rec.sale_order_id.action_confirm()
            elif rec.adjustment_type == 'change_charges':
                rec.state = 'approved'
                # charge_lines = [(5,0,0)]
                # for charge in rec.change_charges_lines:
                #     charge_lines.append((0,0,{
                #         'charge_id': charge.charge_id.id,
                #         'charge_amount': charge.charge_adjustment,
                #     }))
                #     rec.sale_order_id.update({
                #         'charge_ids': charge_lines,
                #     })
                #   rec.state = 'approved'
                    # return method to auto confirm contract order
                    # rec.sale_order_id.action_confirm()
            elif rec.adjustment_type == 'change_items':
                # change_item_lines = [(5,0,0,)]
                # indent_ids = self.env['metrotiles.sale.indention'].search([('name', '=', rec.sale_order_id.name )])
                # for change_items in rec.change_item_lines:
                #     rec.sale_order_id.action_cancel()
                #     for prod in reserved_prod:
                #         prod.unlink()
                #     for indent in indent_ids:
                #         if indent:
                #             indent.unlink()
                #     if len(change_items) > 0:
                #         change_item_lines.append((0,0,{
                #             'location_id': change_items.location_id.id,
                #             'application_id': change_items.application_id.id,
                #             'factory_id': change_items.factory_id.id,
                #             'series_id': change_items.series_id.id,
                #             'product_id': change_items.product_id.id,
                #             'package_id': change_items.package_id.id,
                #             'size': change_items.size,
                #             'variant': change_items.variant,
                #             'price_unit': change_items.price_unit,
                #             'discounts': change_items.column_discounts or ([5,0,0]),
                #             'product_uom_qty': change_items.total_qty,
                #             'qty_delivered': change_items.qty_delivered,
                #         }))
                #     for sale in rec.sale_order_id:
                #         sale.write({'state': 'draft'})
                #     rec.sale_order_id.update({
                #         'order_line': change_item_lines,
                #     })
                rec.state = 'approved'
                    # return method to auto confirm contract order
                    # rec.sale_order_id.action_confirm()
            elif rec.adjustment_type == 'change_discount':
                # sale = self.env['sale.order'].search([('id','=', self.sale_order_id.id)])
                # order_line_ids = self.env['sale.order.line'].search([('order_id', '=', self.sale_order_id.id), ('product_uom_qty', '>', 0)])
                # order_line_ids['discounts'] = rec.column_discounts or [(5,0,0)]
                # sale.update({
                #     'total_discounts': rec.total_discounts or [(5,0,0)]
                # })
                rec.state = 'approved'
                # return method to auto confirm contract order
                # rec.sale_order_id.action_confirm()
            elif rec.adjustment_type == 'change_qty':
                # change_quants_lines = [(5,0,0,)]
                # for pick in spicking:
                #     pick.action_cancel()
                # for change_quants in rec.change_quantity_lines:
                #     for order in rec.sale_order_id:
                #         order.action_cancel()
                #     for prod in reserved_prod:
                #         if reserved_prod:
                #             prod.unlink()
                #     for indent in indent_ids:
                #         if indent:
                #             indent.unlink()
                #     if change_quants.new_qty > 0 and len(change_quants) > 0:
                #         change_quants_lines.append((0,0,{
                #             'location_id': change_quants.location_id.id,
                #             'application_id': change_quants.application_id.id,
                #             'factory_id': change_quants.factory_id.id,
                #             'series_id': change_quants.series_id.id,
                #             'product_id': change_quants.product_id.id,
                #             'package_id': change_quants.package_id.id,
                #             'size': change_quants.size,
                #             'variant': change_quants.variant,
                #             'price_unit': change_quants.price_unit,
                #             'discounts': change_quants.column_discounts or ([5,0,0]),
                #             'product_uom_qty': change_quants.new_qty,
                #             'qty_delivered': change_quants.qty_delivered,
                #         }))
                # for sale in rec.sale_order_id:
                #     sale.update({
                #         'order_line': change_quants_lines,
                #         'state': 'draft',
                #     })
                rec.state = 'approved'
                # return method to auto confirm contract order
                # rec.sale_order_id.action_confirm()
            elif rec.adjustment_type == 'change_vat':
                # vatable = False
                # if rec.new_vat_type == 'vat':
                #     vatable = True
                # else:
                #     vatable
                # rec.sale_order_id.update({
                #     'vatable': vatable,
                # })
                rec.state = 'approved'
                # return method to auto confirm contract order
                # rec.sale_order_id.action_confirm()
            else:
                raise UserError('NO Adjustment Type')
            
            self.write({'status':'approve_admin'})
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('sales.order.adjustment') or 'New'
        request = super(SalesOrderAdjustment, self).create(vals)
    
    
    
    name = fields.Char('SAF Reference', 
        size=32, 
        required=True,
        default='New',
        track_visibility='onchange')
    date_created = fields.Datetime(
        string="Date Created",
        default=fields.Datetime.today())
    sale_order_id = fields.Many2one(
        comodel_name="sale.order", 
        string="Sale Order", 
        store=True
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        related='sale_order_id.partner_id', 
        string="Client"
    )
    sales_ac = fields.Many2one(
        comodel_name="res.users", 
        related='sale_order_id.user_id',
        string="AE"
    )
    date_order = fields.Datetime(string='Order Date', related='sale_order_id.date_order')
    state = fields.Selection(selection=_STATES,
        string='State',
        index=True,
        track_visibility='onchange',
        copy=False,
        default='draft')
    adjustment_type = fields.Selection(
        string="Adjustment Type",
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
    status = fields.Selection(
        selection=_STATUS,
        string="Status",
        index=True,
        track_visibility='onchange',
        copy=False,
        default='active',
    )
    
    column_discounts = fields.Many2many('metrotiles.discount',
                        'metrotiles_discount_column_sales_order_adjustment_rel',
                        string="Column discounts")

    total_discounts = fields.Many2many('metrotiles.discount',
                        string="Discounts")

    current_vat = fields.Many2one(
        comodel_name="account.tax",
        string="Current Vat Type",
        readonly= True,
    )
    new_vat_type = fields.Selection(
        string='Change Vat Type',
        selection=[('vat', 'VATABLE'), ('novat', 'NON-VATABLE')]
    )
    
    cancel_item_lines = fields.One2many(
        comodel_name="metrotiles.cancel.item.lines",
        inverse_name="saf_adjustment_ids",
        string="Cancel Contract Items Page",
        store=True,
    )
    change_charges_lines = fields.One2many(
        comodel_name="metrotiles.change.charges",
        inverse_name="saf_adjustment_ids",
        string="Cancel Contract Items Page",
        store=True,
    )
    change_designer_lines = fields.One2many(
        string="Change Designer/Commission Page",      
        comodel_name='metrotiles.designer.lines',
        inverse_name='saf_adjustment_ids',
        store=True,
    )
    change_architect_lines = fields.One2many(     
        comodel_name='metrotiles.architect.lines',
        inverse_name='saf_adjustment_ids',
        string="Change Architect/Commission Page", 
        store=True,
    )
    change_item_lines = fields.One2many(
        comodel_name="metrotiles.change.item.lines",
        inverse_name="saf_adjustment_ids",
        string="Change Contract Items Page",
        store=True,
    )
    change_quantity_lines = fields.One2many(
        comodel_name="metrotiles.change.quantity.lines",
        inverse_name="saf_adjustment_ids",
        string="change Contract Quantity",
        store=True,
    )
    
    
    
    
    
    