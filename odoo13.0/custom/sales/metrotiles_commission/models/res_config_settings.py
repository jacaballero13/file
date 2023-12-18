from odoo import models, fields, api, exceptions
import json


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    commission_enabled = fields.Boolean(string='Enable')
    commission_account = fields.Many2one('account.account', string='account', config_parameter='account.account')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()

        params = self.env['ir.config_parameter'].sudo()
        commission_enabled = params.get_param('commission_enabled', default=False)
        commission_account = params.get_param('commission_account', default=0)

        res.update({'commission_enabled': commission_enabled, 'commission_account': int(commission_account)})

        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()

        self.env['ir.config_parameter'].sudo().set_param(
            "commission_enabled",
            self.commission_enabled)

        self.env['ir.config_parameter'].sudo().set_param(
            "commission_account",
            self.commission_account.id)
