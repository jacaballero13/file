# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class Discounts(models.Model):
    _inherit = "metrotiles.discount"
    _order = 'name desc'

class SaleOrderLineInherit(models.Model):
    _inherit = 'sale.order.line'

    dian_field_temp_del = fields.Float() #Remove later if all past transactions have been fixed
    
    #Remove later if all past transactions have been fixed
    @api.onchange('dian_field_temp_del')
    def dian_field_delivered_qty(self):
        for rec in self:
            if rec.order_id.state == 'sale':
                if rec.dian_field_temp_del >=0:
                    rec._cr.execute(
                        """ UPDATE sale_order_line set qty_delivered = %s WHERE id = %s""" %(rec.dian_field_temp_del,rec._origin.id if rec._origin.id else '0')
                        )

class SalesOrderInherit(models.Model):
    _inherit = 'sale.order'

    company_type = fields.Char(string="Company Type", compute='get_company_type')
    partner_id = fields.Many2one(comodel_name='res.partner', tracking=True)
    category_id = fields.Many2one('product.category', string="Category", domain="[('product_sub_category', '>', 0)]")
    product_sub_category = fields.Many2one('product.sub.category', string="Sub Category")

    @api.onchange('category_id')
    def _get_product_sub_category(self):
        for field in self:
            field.product_sub_category = None
            return {'domain': {"product_sub_category": [("category_id", "=", field.category_id.id)]}}

    # @api.depends('partner_id')
    def get_company_type(self):
        for rec in self:
            if rec.partner_id.company_type == 'person':
                rec.company_type = "Individual"
            else:
                rec.company_type = "Company"
    
    @api.model
    def create(self, vals):
        quot_type = vals.get('quotation_type')
        
        if quot_type == 'sample':
            vals['name'] = self.env['ir.sequence'].next_by_code('s.o.sample.sequence')
            
        if quot_type == 'regular':
            vals['name'] = self.env['ir.sequence'].next_by_code('s.o.regular.sequence')
        
        if quot_type == 'installation':
            vals['name'] = self.env['ir.sequence'].next_by_code('s.o.installation.sequence')
        
        return super(SalesOrderInherit, self).create(vals)