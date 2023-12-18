from ast import literal_eval
from odoo import models, fields, api, exceptions
import json

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    stock_locations = fields.Many2many('stock.location', 'res_config_stock_locations_rel', string='Stock Locations')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()

    #     params = self.env['ir.config_parameter'].sudo()
    #     print(params.get_param('stock_locations', default='[]'))
    #     res.update({'stock_locations': eval(params.get_param('stock_locations', default='[]'))})
        stock_locations = self.env['ir.config_parameter'].sudo().get_param('metrotiles_reservation.stock_locations')
        print(stock_locations)
        res.update(stock_locations=[(6,0, literal_eval(stock_locations))],
        )
        return res

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        print(self.stock_locations.ids)
        self.env['ir.config_parameter'].sudo().set_param("metrotiles_reservation.stock_locations", self.stock_locations.ids)
        return res
        # ids = []

        # for location in self.stock_locations:
        #     ids.append(location.id)

        # self.env['ir.config_parameter'].sudo().set_param(
        #     "stock_locations", ids)