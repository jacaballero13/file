from odoo import models, fields, api, exceptions


class Designer(models.Model):
    _inherit = 'metrotiles.designer'
    _order = 'designer_sale_id desc'

    designer_sale_id = fields.Many2one(string='sale', comodel_name='sale.order')
    date_order = fields.Datetime(string="Date Order", compute="get_conract_details")
    partner_id = fields.Many2one('res.partner', string="Customer", compute="get_conract_details")
    material_total = fields.Float('Product Net Total', compute="get_conract_details")


    @api.depends('designer_sale_id')
    def get_conract_details(self):
        for rec in self:
            if rec.designer_sale_id:
                rec.date_order = rec.designer_sale_id.date_order
                rec.partner_id = rec.designer_sale_id.partner_id.id
                rec.material_total = rec.designer_sale_id.material_total