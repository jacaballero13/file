# -*- coding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID, _
from datetime import datetime


class MrpProduction(models.Model):
    _inherit = 'mrp.production'
    
    @api.model_create_multi
    def create(self, vals_list):
        """
            Create a new record for a model Mrp Production
            @param values: provides a data for new record
    
            @return: returns a id of new record
        """
        for mrp_production in vals_list:
            if mrp_production.get('origin'):
                sale_order = self.env['sale.order']
                order_id = sale_order.search([('name','=', mrp_production['origin'])])
                for order in order_id:
                    if order_id:
                        date_delivery = order['commitment_date']
                        mrp_production['date_deadline'] = date_delivery

        return super(MrpProduction, self).create(vals_list)


