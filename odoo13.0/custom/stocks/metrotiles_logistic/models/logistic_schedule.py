# -*- coding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError

class MetrotilesLogisticSchedule(models.Model):
    _name = 'calendar.events'
    _rec_name = 'name'
    
    #Contract Details
    name = fields.Char('Reference')
    wh_ref = fields.Many2one('stock.picking', 'WH Reference')
    delivery_contract_id = fields.Many2one(comodel_name="delivery.contract", string="Delivery Contract", store=True,)
    sale_order_id = fields.Many2one(comodel_name='sale.order', string="Sales Order", store=True, track_visibility="onchange", )
    warehouse_id = fields.Many2one(comodel_name='stock.warehouse', string="Warehouse", store=True)
    sales_ac = fields.Many2one(comodel_name= 'res.users', string="Account Coordinator", store=True)
    partner_id = fields.Many2one(comodel_name='res.partner', string="Client", store=True)
    responsible_user = fields.Many2one(comodel_name='res.users', string="Responsible", store=True)
    delivery_no = fields.Char(string='DR No.', size=32, default='New')
    # Delivery Schedule
    delivery_date = fields.Datetime('Delivery Date')
    delivery_area = fields.Char(string='Delivery Area')
    track_id = fields.Many2one('fleet.vehicle', string="Track Type")
    trip = fields.Selection([('first_trip', 'First Trip'), ('sec_trip', 'Second Trip')],
                            string="Trip")
    
    quotation_type = fields.Selection([('regular', 'Regular'), ('installation', 'Installation'),
                                ('sample','Sample'), ('foc', 'Free of Charge'),],
								string="Quotation type",)
    has_started = fields.Selection(
		string='Has Started?',
		selection=[('no', 'No'), ('yes', 'Yes')]
	)
    
    dr_type = fields.Selection(
        string='Type of Operation',
        selection=[
                ('delivery', 'Delivery'),
                ('pullout', 'Regular Pullout'),
                ('transfer', 'Stock Trasnfer')]
    )
