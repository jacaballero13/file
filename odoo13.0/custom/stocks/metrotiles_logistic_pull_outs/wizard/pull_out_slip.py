from typing import Sequence
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class PullOutSlip(models.TransientModel):
    _name = 'pull.out.slip'

    #name = fields.Char(string='Pull Out No.')
    warehouse_id = fields.Many2one(comodel_name='stock.warehouse', string='Warehouse')
    pu_date = fields.Date(string="Pull Out Date")
    pu_type = fields.Char(string="Pull Out Type")
    track_id = fields.Many2one('fleet.vehicle', string="Truck")	
    trip = fields.Selection([('first_trip', 'First Trip'), ('sec_trip', 'Second Trip')],
                            string="Trip")
    
    def get_contract_no(self):
        context = dict(self._context or {})
        active_id = context.get('active_id', []) or []
        contract = self.env['metrotiles.pull.outs'].browse(active_id)
        if active_id:
            return contract.sale_order_id.name
        
    
    @api.model
    def default_get(self,default_fields):
        res = super(PullOutSlip, self).default_get(default_fields)
        context = self._context
        pu_details = {
            'pu_date': context.get('pu_date'),
            'pu_type': context.get('pu_type'),
            'track_id': context.get('track_id'),
            'trip': context.get('trip'),
            'warehouse_id': context.get('warehouse_id')
        }
        
        res.update(pu_details)
        return res
        
    contract_no = fields.Char(string="Contract", default=get_contract_no)
    
    def generate_slip(self):
        context = self._context
        active_id = context.get('active_id', [])
        pull_outs_obj = self.env['metrotiles.pull.outs'].browse(active_id)
        stock_obj = self.env['stock.picking']
        lines = []
        code = self.env['ir.sequence'].next_by_code('logistic.pull.outs')
        pull_outs_obj.write({'pull_out_no': code})
        
        if pull_outs_obj:
            stock_obj.search([('origin', '=', pull_outs_obj.sale_order_id.name),('name','ilike','OUT')])\
                .update({'pull_out_no':pull_outs_obj.pull_out_no})
                
            pull_outs_obj.update({'pull_out_no':code,
                            'state': 'done'})
            