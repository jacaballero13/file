from odoo import models, fields, api


class CalendarEvents(models.Model):
    _inherit = 'calendar.events'
    
    
    pullout_type = fields.Selection(
                    string='Pull Out Type',
                    selection=[('saf', 'Sales Adjustment'), ('sample', 'Return Samples'),
                            ('cancel', 'Cancelled Contracts')])
    pullout_contract_id = fields.Many2one('metrotiles.pull.outs', string="Pull Outs")