# -*- coding: utf-8 -*-

from odoo import models, fields
import datetime
import logging
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)

class DemoClass(models.Model):
    _name = 'cron.sales.order'

    def cron_sales_order_expiration(self):
        sales_obj = self.env['sale.order'].search([('state','=','draft')])
        
        for rec in sales_obj:
            if datetime.date.today() > rec.validity_date:
                rec.action_cancel()
