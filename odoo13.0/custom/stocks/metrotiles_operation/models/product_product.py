from odoo import models, fields, api, _


class ProductProductInherit(models.Model):
    _inherit = 'product.product'
    _order = 'series_name ASC'

    series_name = fields.Char(string="Series", compute="_compute_series_name", store=True)

    @api.depends('series_id')
    def _compute_series_name(self):
        for template in self:
            template.series_name = template.series_id.name

    on_sale = fields.Boolean("Sale", help="This product will be On Sale will be use in filtering", store=True)
    on_discontinue = fields.Boolean("Discontinue", help="This product will be Discontinued and to be use in filtering", store=True)
    remarks = fields.Selection([
                                ('sale', 'Sale'),
                                ('discontinue', 'Discontinued'),
                                ], string="Remarks", readonly=True, compute='set_product_remarks', store=True)

    # added origin and finish
    origin = fields.Char(string="Origin")
    finish = fields.Char('Finish')

    factory_id = fields.Many2one(comodel_name="res.partner", string="Factory", compute="get_factory", store=True,)

    @api.depends('seller_ids')
    def get_factory(self):
        for record in self:
            for seller in record.seller_ids:
                if len(seller) > 0:
                    record.update({
                        'factory_id': seller[0].name
                    })  

    @api.depends('on_sale', 'on_discontinue')
    def set_product_remarks(self):
        for rec in self:
            if rec.on_sale == True:
                rec.remarks = 'sale'
            elif rec.on_discontinue == True:
                rec.remarks = 'discontinue'

            else:
                rec.remarks = None
