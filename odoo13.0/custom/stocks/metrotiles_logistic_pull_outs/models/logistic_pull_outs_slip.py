from odoo import models, fields, api

class PullOutSlip(models.Model):
    _name = 'metrotiles.pull.out.slips'
    
    # contract_no 
    pu_no = fields.Char(string='Pull Out No', readonly=True)
    pu_date = fields.Char(string='Date')
    warehouse_id = fields.Many2one(comodel_name='stock.location', string='Warehouse')
    sale_order_id = fields.Many2one(comodel_name='sale.order', string="Contract No.", store=True, track_visibility="onchange", readonly=True)
    pu_type = fields.Selection([('regular', 'Regular'), ('installation', 'Installation')],
                                default="regular",
                                string="Type", related="sale_order_id.quotation_type")
    sales_ac = fields.Many2one(comodel_name= 'res.users', related="sale_order_id.sales_ac", string="Account Coordinator", store=True, readonly=False)
    partner_id = fields.Many2one(comodel_name='res.partner', related="sale_order_id.partner_id", string="Client", store=True)
    status = fields.Selection(string='Status', selection=[('not_started', 'NOT STARTED YET'), ('received', 'RECEIVED'),], default='not_started')
    
    