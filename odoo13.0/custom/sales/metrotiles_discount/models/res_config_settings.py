from odoo import models, fields, api, exceptions
import json


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    discount_enabled = fields.Boolean(string='Discount')
    discount_account = fields.Many2one('account.account', string='account', config_parameter='account.account')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()

        params = self.env['ir.config_parameter'].sudo()
        discount_enabled = params.get_param('discount_enabled', default=False)
        discount_account = params.get_param('discount_account', default=0)

        res.update({'discount_enabled': discount_enabled, 'discount_account': int(discount_account)})

        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()

        self.env['ir.config_parameter'].sudo().set_param(
            "discount_enabled",
            self.discount_enabled)

        self.env['ir.config_parameter'].sudo().set_param(
            "discount_account",
            self.discount_account.id)
