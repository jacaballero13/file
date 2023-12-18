from odoo import models, fields, api, exceptions
import json


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    installation_account = fields.Many2one('account.account', string='Account', config_parameter='account.account')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()

        params = self.env['ir.config_parameter'].sudo()
        account_id = params.get_param('installation_account', default=0)

        res.update({'installation_account': int(account_id)})

        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()

        self.env['ir.config_parameter'].sudo().set_param(
            "installation_account",
            self.installation_account.id)
