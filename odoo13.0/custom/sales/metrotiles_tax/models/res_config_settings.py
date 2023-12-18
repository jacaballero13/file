from odoo import models, fields, api, exceptions
import json


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    vat_enabled = fields.Boolean(string='VAT')
    vat = fields.Many2one('account.tax', string='VAT', config_parameter='account.tax')
    vat_amount = fields.Float('vat_amount', default=0.0)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()

        params = self.env['ir.config_parameter'].sudo()
        vat_enabled = params.get_param('vat_enabled', default=False)
        vat = params.get_param('vat', default=0)
        res.update({'vat_enabled': vat_enabled, 'vat': int(vat)})

        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()

        self.env['ir.config_parameter'].sudo().set_param(
            "vat_enabled",
            self.vat_enabled)

        self.env['ir.config_parameter'].sudo().set_param(
            "vat",
            self.vat.id)

        self.env['ir.config_parameter'].sudo().set_param(
            "vat_amount",
            self.vat.amount)