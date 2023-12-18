# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.move.line'

    category_id = fields.Many2one('metrotiles.category', string="Wall/Location")
    wall = fields.Many2one('metrotiles.wall', string='Wall ID')
    pallet_id = fields.Many2one('metrotiles.pallet', string="Pallet ID")

    @api.onchange('category_id')
    def wall_category(self):
        for field in self:
            field.wall = None
            return {'domain': {"wall": [("category_id", "=", field.category_id.id)]}}

