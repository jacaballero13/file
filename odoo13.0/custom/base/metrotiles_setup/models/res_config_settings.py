from odoo import models, fields, api, exceptions
import json


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    @api.model
    def _metrotiles_setup(self):
        return
    #     print('METROTILES SETUP START...')
    #     currency = self.sudo().env['res.currency'].search([('name', '=ilike', 'PHP')])
    #     currency.update({'active': True})
    #     currency_id = currency.id
    #     data = {
    #         'group_product_variant': True,
    #         'group_uom': True,
    #         'group_product_pricelist': True,
    #         'group_sale_delivery_address': True,
    #         'group_sale_order_template': True,
    #         'use_quotation_validity_days': True,
    #         'group_multi_currency': True,
    #         'quotation_validity_days': 15,
    #         'currency_id': currency_id
    #     }
    #
    #     self.search([], order='id desc')[0].sudo().update(data)
    #
    #     print('- VALUES SET')
    #
    #     self.env['ir.config_parameter'].sudo().set_param(
    #         "group_product_variant", True)
    #
    #     self.env['ir.config_parameter'].sudo().set_param(
    #         "group_uom", 'True')
    #
    #     self.env['ir.config_parameter'].sudo().set_param(
    #         "group_product_pricelist", True)
    #
    #     self.env['ir.config_parameter'].sudo().set_param(
    #         "group_sale_delivery_address", True)
    #
    #     self.env['ir.config_parameter'].sudo().set_param(
    #         "group_sale_order_template", True)
    #
    #     self.env['ir.config_parameter'].sudo().set_param(
    #         "use_quotation_validity_days", True)
    #
    #     self.env['ir.config_parameter'].sudo().set_param(
    #         "use_quotation_validity_days", True)
    #
    #     self.env['ir.config_parameter'].sudo().set_param(
    #         "group_multi_currency", True)
    #
    #     self.env['ir.config_parameter'].sudo().set_param(
    #         "quotation_validity_days", 15)
    #
    #     self.env['ir.config_parameter'].sudo().set_param(
    #         "currency_id", currency_id)
    #
    #     print('- SETUP END')
    #
    # @api.model
    # def get_values(self):
    #     res = super(ResConfigSettings, self).get_values()
    #
    #     params = self.env['ir.config_parameter'].sudo()
    #
    #     res.update({
    #         'group_product_variant': bool(params.get_param('group_product_variant', 'False')),
    #         'group_uom': bool(params.get_param('group_uom', 'False')),
    #         'group_product_pricelist': bool(params.get_param('group_product_pricelist', 'False')),
    #         'group_sale_delivery_address': bool(params.get_param('group_sale_delivery_address', 'False')),
    #         'group_sale_order_template': bool(params.get_param('group_sale_order_template', 'False')),
    #         'use_quotation_validity_days': bool(params.get_param('use_quotation_validity_days', 'False')),
    #         'group_multi_currency': bool(params.get_param('group_multi_currency', 'False')),
    #         'quotation_validity_days': int(params.get_param('quotation_validity_days', 0)),
    #         'currency_id': int(params.get_param('currency_id', 0))
    #     })
    #
    #     return res