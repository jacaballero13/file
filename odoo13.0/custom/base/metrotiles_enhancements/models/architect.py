from odoo import models, fields, api, exceptions


class Architect(models.Model):
    _inherit = 'metrotiles.architect'
    _order = 'architect_sale_id desc'


    architect_sale_id = fields.Many2one(string='sale', comodel_name='sale.order', track_visibility='onchange')
    date_order = fields.Datetime(string="Date Order", compute="get_conract_details")
    partner_id = fields.Many2one('res.partner', string="Customer", compute="get_conract_details")
    material_total = fields.Float('Product Net Total', compute="get_conract_details")


    @api.depends('architect_sale_id')
    def get_conract_details(self):
        for rec in self:
            if rec.architect_sale_id:
                rec.date_order = rec.architect_sale_id.date_order
                rec.partner_id = rec.architect_sale_id.partner_id.id
                rec.material_total = rec.architect_sale_id.material_total