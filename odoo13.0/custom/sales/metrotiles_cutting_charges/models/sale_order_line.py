# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    
    cutting_lines = fields.One2many(
        comodel_name='product.cutting.charges.lines',
        inverse_name='cutting_charge_sale_id',
        string='Cutting Charges',
        copy=True
    )
    
    cutting_charges_amount = fields.Float(
        string="Cutting Charges Total",
        default=0.0,
        compute="_cutting_total_charges",
        store=True
    )
    cutting_charge = fields.Many2one('metrotiles.name_charges', store=True,)
    
    @api.depends('cutting_lines.cutting_charges')
    def _cutting_total_charges(self):
        total_cutting_charges = 0.0
        for rec in self:
            for cutting in rec.cutting_lines:
                total_cutting_charges += cutting.cutting_charges
                
            rec.update({'cutting_charges_amount': total_cutting_charges })
            
    
    # @api.model
    # def create(self, values):
    #     """
    #         Create a new record for a model SaleOrder
    #         @param values: provides a data for new record
    
    #         @return: returns a id of new record
    #     """
    #     lines = []
    #     for rec in self:
    #         if rec.cutting_charges_amount > 0:
    #             charge_ids = self.env['metrotiles.name_charges'].search([])
    #             lines.append((0,0,{
    #                 'charge_id': charge_ids[1],
    #                 'charge_amount': rec.cutting_charges_amount,
    #             }))
    #             rec.update({
    #                 'charge_ids': lines
    #             })            
    #     return super(SaleOrder, self).create(values)

    def write(self, values):
        datas = []
        lines = []
        order_line_ids = self.env['sale.order.line'].sudo().search([('order_id', '=', self.id), ('to_fabricate', '=', True)])
        for record in self:
            for items in order_line_ids:
                if items.to_fabricate and len(record.cutting_lines) <= 0:
                    lines.append((0,0,{
                        'product_id': items.product_id.id,
                        'location_id': items.location_id.id,
                        'application_id': items.application_id.id,
                        'factory_id': items.factory_id.id,
                        'series_id': items.series_id.id,
                        'variant': items.variant,
                        'quantity': items.product_uom_qty,
                        'bom': items.bom.id,
                    }))
                    values['cutting_lines'] = lines
                
                if not record.charge_ids and record.cutting_charges_amount > 0:
                    datas.append((0,0,{
                        # 'charge_id': charge_ids.name,
                        'charge_amount': record.cutting_charges_amount,
                    }))
                    values['charge_ids'] = datas
        return  super(SaleOrder, self).write(values)