from odoo import models, fields, api, exceptions
import json


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    base_category_id = fields.Many2one('product.category', string='Base Catergory id')
    res_cat_vendor_tag_id = fields.Many2one('res.partner.category', string='Vendor category_id')
