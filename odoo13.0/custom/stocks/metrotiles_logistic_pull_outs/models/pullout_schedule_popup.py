from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError


class PulloutSchedulePopup(models.TransientModel):
    _name = 'pullout.schedule.popup'
    
    pullout_contract_id = fields.Many2one('metrotiles.pull.outs', string="Pull Outs")
    commitment_date = fields.Datetime('Pull Out Date')
    track_id = fields.Many2one('fleet.vehicle', string="Track Type")
    trip = fields.Selection([('first_trip', 'First Trip'), ('sec_trip', 'Second Trip')],
                            default="first_trip", string="Trip")
    warehouse_id = fields.Many2one(comodel_name='stock.warehouse', string="Warehouse", store=True, readonly=False)
    pullout_type = fields.Selection(
        string='Pull Out Type',
        selection=[('saf', 'Sales Adjustment'), ('sample', 'Return Samples'),
                    ('cancel', 'Cancelled Contracts')]
    )
    sale_order_id = fields.Many2one(comodel_name='sale.order', string="Sales Order", store=True, track_visibility="onchange", readonly=True)

    def action_confirm(self):
        active_ids = self._context.get('active_ids', [])
        pullout_contract_ids = self.env['metrotiles.pull.outs'].browse(active_ids)
        contract_ref = pullout_contract_ids.sale_order_id.name

        #Update recorde based on SO reference to Delivery Orders
        pullout_scheudle = self.pullout_contract_id.update({
                    'dt_created': self.commitment_date,
                    'track_id': self.track_id.id,
                    'trip': self.trip,
                })
        print(pullout_scheudle)
        # create records to lineup schedule calendar
        for each in pullout_contract_ids:
            schedule = self.env['calendar.events'].create({
                'pullout_contract_id': pullout_contract_ids.id,
                'delivery_date': self.commitment_date,
                'dr_type': 'pullout',
                'name': each.name,
                'sale_order_id': each.sale_order_id.id,
                'quotation_type': each.quotation_type,
                'warehouse_id': each.warehouse_id.id,
                'sales_ac': each.sales_ac.id,
                'partner_id': each.partner_id.id,
                'track_id': each.track_id.id,
                'trip': each.trip,
                'responsible_user': each.responsible_user.id,
            })
            print(schedule)