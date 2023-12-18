from odoo import models, fields, api, _
from odoo.exceptions import UserError


class NameCharges(models.Model):
    _name = 'metrotiles.name_charges'
    _description = 'Metrotiles Charge Name'

    name = fields.Char(string="Charge Name")
    description = fields.Text(string="Notes")
    account_charge_id = fields.Many2one('account.account', string="Account Code")
