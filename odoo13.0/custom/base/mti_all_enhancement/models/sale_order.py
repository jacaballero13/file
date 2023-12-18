from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'


    delivery_charge = fields.Char(compute='_get_delivery_charges_compute')
    interior_designer = fields.Char(compute='_get_delivery_charges_compute')
    architect = fields.Char(compute='_get_delivery_charges_compute')
    quotation_type = fields.Selection(selection_add=[('foc', 'Free of Charge')])
    saf_count = fields.Integer(string='Sales Adjustment Form', compute='get_saf_count')
    
    def get_saf_count(self):
        count = self.env['sales.order.adjustment'].search_count([('sale_order_id', '=', self.id)])
        self.saf_count = count
    # Redirect to SAF adjustment
    def open_sales_adjustment(self):
        return {
            'name': _('Sales Adjustment Form'),
            'domain': [('sale_order_id', '=', self.id)],
            'view_type': 'form',
            'res_model': 'sales.order.adjustment',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }

    @api.depends('charge_ids','designer_ids','architect_ids')
    def _get_delivery_charges_compute(self):
        self.computed_delivery =''
        self.computed_designer = ''
        self.computed_architect = ''
        
        
        for rec in self:
            dr_charges = '' 
            designer_charges = ''
            architect_charges = ''
            #Delivery Charges
            for charges in rec.charge_ids:
                if len(charges)>0:
                    dr_charges = dr_charges + str(charges.charge_id.name) + ',' +str(charges.charge_amount) + " "
            
            #Desginer Charges
            for designer in rec.designer_ids:
                if len(designer)>0:
                    designer_charges = designer_charges + str(designer.designer_id.name)
                
            # Architect Charges
            for architect in rec.architect_ids:
                if len(architect)>0:
                    architect_charges = architect_charges + str(architect.architect_id.name)
        
        
            rec.delivery_charge = dr_charges
            rec.interior_designer = designer_charges
            rec.architect = architect_charges