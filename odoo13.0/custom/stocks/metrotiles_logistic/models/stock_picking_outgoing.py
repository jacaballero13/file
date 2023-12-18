from odoo import api, models, fields
import logging
from datetime import datetime, timedelta
from odoo.exceptions import UserError

class StockPicking(models.Model):
        _inherit = 'stock.picking'

        delivery_contract_id = fields.Many2one("delivery.contract", string="Delivery Contract")
        commitment_date = fields.Datetime('Delivery Date')
        delivery_area = fields.Many2one('delivery.area', string='Delivery Area')
        track_id = fields.Many2one('fleet.vehicle', string="Track Type")
        trip = fields.Selection([('first_trip', 'First Trip'), ('sec_trip', 'Second Trip')],
                                default="first_trip", string="Trip")

        shipment_ref = fields.Char("Shipment No.")
        container_ref = fields.Char("Cotainer No.")
        bol_ref = fields.Char("BL No.")
        xx_ets = fields.Date(string="ETS")
        xx_eta = fields.Date(string="ETA")

        quotation_type = fields.Selection([
                        ('regular', 'Regular'), 
                        ('installation', 'Installation'),
                        ('foc', 'Free of Charge'),
                        ('sample', 'Sample')],
                        string="Quotation type",compute="get_contract_type", store=True)
        has_started = fields.Selection(
                string='Has Started',
                default='no',
                selection=[('no', 'No'), ('yes', 'Yes')])
        acknowledge = fields.Selection(
                string='Acknowledge',
                default='false',
                selection=[('false', 'False'), 
                        ('true', 'True')]
                )
        delivery_no = fields.Char(string='DR No.',size=32, related="delivery_contract_id.delivery_no", default='New', domain=[('picking_type_code', '=', 'outgoing')])

        # Added  compute field in order to filter contract type during return
        @api.depends('group_id')
        def get_contract_type(self):
                sale_order  = self.env['sale.order'].search([('name','=', self.group_id.name)])
                if sale_order:
                    self.quotation_type = sale_order.quotation_type
                    
        @api.model
        def create(self, values):
            """
                Create a new record for a model ModelName
                @param values: provides a data for new record
        
                @return: returns a id of new record
            """
            sale_order  = self.env['sale.order'].search([('name','=', values.get('origin'))])
            if sale_order:
                for sale in sale_order:
                    types = sale.quotation_type
                    values['quotation_type'] = types
            else:
                values['quotation_type'] = None

            return super(StockPicking, self).create(values)
        
            
        