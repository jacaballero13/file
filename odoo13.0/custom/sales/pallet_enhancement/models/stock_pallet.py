# -*- coding: utf-8 -*-

from re import L
from odoo import models, fields, api
from odoo.exceptions import UserError
class StockPallet(models.Model):
    _inherit = 'stock.pallet'
    _rec_name = 'name'
    
    name = fields.Char()

class SaleOrder(models.Model):
    _inherit = 'sale.order.line'
    
    @api.onchange('product_id')
    def _get_pallet_details(self):
        for rec in self:
            for line in rec.product_id.pallet_ids:
                stock_pallet=self.env['stock.pallet'].search([('pallet','=',line.pallet.id)])
                check_availiability = self.env['stock.quant'].sudo().search([('product_id','=', rec.product_id.id), ('location_id', '=', line.location_id.id), ('package_id', '=', line.pallet.id)])
                if check_availiability and len(line.pallet.quant_ids) > 0 and check_availiability.on_hand > 0:
                    stock_pallet.update({'name': '[P%s] - (On Stock - %d)'%(line.pallet.name, check_availiability.on_hand)})
                else:
                    stock_pallet.update({'name':'[%s - No Stock]'%(line.pallet.name)})