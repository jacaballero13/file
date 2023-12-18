from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError

_STATES = [
	('draft', 'Not yet Ready'),
	('done', 'Done')
]

class MetrotilesPullOuts(models.Model):
    _name = 'metrotiles.pull.outs'
    _inherit = ['mail.thread']
    _order = 'create_date desc'

    name = fields.Char(compute='get_so_contract', readonly=True)
    pull_out_no = fields.Char(string='Pull Out No.', copy=False, readonly=True, store=True,)
    sale_order_id = fields.Many2one(comodel_name='sale.order', string="Sales Order", store=True, track_visibility="onchange")
    quotation_type = fields.Selection([('regular', 'Regular'), ('installation', 'Installation'),
                                ('sample', 'Sample')],
                                default="regular",
                                string="Type", related="sale_order_id.quotation_type")
    pullout_type = fields.Selection(
        string='Pull Out Type',
        selection=[('saf', 'Sales Adjustment'), ('sample', 'Return Samples'),
                ('cancel', 'Cancelled Contracts')
                ]
    )
    manual_pos = fields.Char("Manual POS")
    manual_pos_date = fields.Datetime("Manual POS Date")
    warehouse_id = fields.Many2one(comodel_name='stock.warehouse', related="sale_order_id.warehouse_id", string="Warehouse", store=True, readonly=False)
    sales_ac = fields.Many2one(comodel_name= 'res.users', related="sale_order_id.sales_ac", string="Account Coordinator", store=True)
    partner_id = fields.Many2one(comodel_name='res.partner', related="sale_order_id.partner_id", string="Client", store=True)
    dt_created = fields.Date('Date', default=datetime.today())
    responsible_user = fields.Many2one('res.users', 'Responsible', default=lambda self: self.env.user)

    site_contact = fields.Char(related="sale_order_id.site_contact", string="Site Contact Person")
    site_number = fields.Char(related="sale_order_id.site_number", string="Site Contact Number")
    site_permit = fields.Boolean(string="Requires Permit", related="sale_order_id.site_permit")
    r_permit = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Requires Permit", compute="is_permit")	

    track_id = fields.Many2one('fleet.vehicle', string="Truck Type")	
    trip = fields.Selection([('first_trip', 'First Trip'), ('sec_trip', 'Second Trip')],
                            default="first_trip", string="Trip")
    
    delivery_count = fields.Integer(string='Appointment', compute='get_delivery_schedule_count')
    pull_out_cal = fields.Integer(string='Calender', compute='get_delivery_schedule_count')
    is_editable = fields.Boolean(string='Is editable',
                                compute="_compute_is_editable",
                                readonly=True)
    state = fields.Selection(selection=_STATES,
                                string='Status',
                                index=True,
                                track_visibility='onchange',
                                required=True,
                                copy=False,
                                default='draft')
    approve_refused_reason = fields.Char('Refused reason', readonly=True, copy=False, tracking=1)
    pu_order_lines = fields.One2many('metrotiles.pull.outs.lines', 'pull_out_id', string="Contract Order Lines", 
									required=True, store=True)
    schedule_count = fields.Integer(string='Pull Out Schedule', compute='get_schedule_count')
    @api.depends('sale_order_id', 'partner_id')
    def get_so_contract(self):
        for contract in self:
            sale_order = contract.sale_order_id.name or ""
            partner = contract.partner_id.name or ""
            contract.name = "LU|[%s] %s" % (sale_order, partner)
            
    @api.depends('r_permit')
    def is_permit(self):
        for record in self:
            if record.site_permit == True:
                record.r_permit = 'yes'
            else:
                record.r_permit = 'no'
                
    def get_delivery_schedule_count(self):
        count = self.env['stock.picking'].search_count([('pull_out_no', '=',self.pull_out_no)])
        self.delivery_count = count
        
    @api.depends('state')
    def _compute_is_editable(self):
        for rec in self:
            if rec.state in ('to_approve', 'approved', 'rejected'):
                rec.is_editable = False
            else:
                rec.is_editable = True
    
    
    def generate_pull_out_slip(self):
        code = self.env['ir.sequence'].next_by_code('logistic.pull.outs')
        view_id = self.env.ref('metrotiles_logistic_pull_outs.view_generate_pull_out_slip_form')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Pull Out Details',
            'res_model': 'pull.out.slip',
            'view_id': view_id.id,
            'view_mode': 'form',
            'target': 'new',
            'context':{
                'pu_no': "%s|[%s]" % (code,self.sale_order_id.name or ""),
                'pu_date': self.dt_created,
                'pu_type': self.quotation_type,
                'trip': self.trip,
                'track_id': self.track_id.id,
                'warehouse_id': self.warehouse_id.id,
                
            }
        }
        
    def open_delivery_schedule(self):
        return {
            'name': _('Pull Outs Schedule'),
            'domain': [('pull_out_no', '=', self.pull_out_no)],
            'view_type': 'form',
            'res_model': 'stock.picking',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }
        
    # Smart button that be redirected to Logistic Calendar
    def open_pullout_schedule(self):
        return {
            'name': _('Pull Out Schedule'),
            'domain': [('pullout_contract_id', '=', self.id)],
            'view_type': 'calendar',
            'res_model': 'calendar.events',
            'view_id': False,
            'view_mode': 'tree,calendar',
            'type': 'ir.actions.act_window',
        }
    # Count Lineup Scheudle Pullouts
    def get_schedule_count(self):
        count = self.env['calendar.events'].search_count([('pullout_contract_id', '=', self.id)])
        self.schedule_count = count
        
    # method to create pullout schedule
    def generate_pull_out_schedule(self):
        view_id = self.env.ref('metrotiles_logistic_pull_outs.pullout_schedule_popup_form')
        if view_id:
            req_view_id = {
                'name': "Create Pullout Schedule",
                'view_mode': 'form',
                'view_id': view_id.id,
                'view_type': 'form',
                'res_model': 'pullout.schedule.popup',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'context': {
                    'default_commitment_date': self.dt_created,
                    'default_warehouse_id': self.warehouse_id.id,
                    'default_pullout_type': self.pullout_type,
                    'default_sale_order_id': self.sale_order_id.id,
                    'default_pullout_contract_id': self.id,
                }
            }
        return req_view_id

class MetrotilesPullOutsLine(models.Model):
    _name = 'metrotiles.pull.outs.lines'



    pull_out_id = fields.Many2one('metrotiles.pull.outs', string="Delivery Contract")

    name = fields.Char(string="Product", store=True)
    product_id = fields.Many2one('product.product', string="Product", store=True)

    location_id = fields.Many2one(comodel_name='metrotiles.location', string="Location", store=True)
    application_id = fields.Many2one(comodel_name='metrotiles.application', string="Application", store=True)

    factory_id = fields.Many2one(comodel_name='res.partner', string='Factory',store=True)
    series_id = fields.Many2one(comodel_name='metrotiles.series', string='Series', readonly=False,store=True)

    variant = fields.Char(string="Variant")
    size = fields.Char(string="Sizes (cm)")

    qty_delivered = fields.Integer(string="Qty Delivered", default=0, store=True)
    product_uom_qty = fields.Integer(string="Contract Qty",readonly=True, default=None)
    pull_out_qty = fields.Integer(string="Pull Out Qty", store=True)
    