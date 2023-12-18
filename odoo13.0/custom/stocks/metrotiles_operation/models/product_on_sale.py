from odoo import models, fields, api, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    factory_id = fields.Many2one(comodel_name="res.partner", string="Factory", compute="get_factory", store=True,)

    @api.depends('name')
    def get_factory(self):
        for record in self:
            for seller in record.variant_seller_ids:
                if len(seller) > 0:
                    record.update({
                        'factory_id': seller.name
                    })
