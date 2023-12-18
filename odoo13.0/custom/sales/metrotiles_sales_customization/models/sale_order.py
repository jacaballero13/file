# -*- coding: utf-8 -*-

import datetime
import dateutil.parser
from odoo import models, fields, api
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta



class MetrotilesSalesCustom(models.Model):
    _inherit = 'sale.order'
    
    invoice_address = fields.Char(string='Invoice Address')
    delivery_address = fields.Char(string='Delivery Address')
    
    @api.onchange('partner_id')
    def fill_up_client_details(self):
        if self.partner_id:
            for rec in self.partner_id:
                self.delivery_address = rec.delivery_address
                self.invoice_address = rec.invoice_address

    
    # @api.onchange('date_order')
    # def _check_change(self):
    #     if self.date_order:
    #         date_1= (datetime.stroftime(self.date_order, '%Y-%m-%d')+relativedelta(days =+ 15))
    #         self.validity_date = date_1
        
    @api.model
    def default_get(self, fields):
        res = super(MetrotilesSalesCustom, self).default_get(fields)
        current_date = datetime.datetime.now().date()
        new_date = current_date + datetime.timedelta(days=15)
        res['validity_date'] = new_date
            
        return res
    
