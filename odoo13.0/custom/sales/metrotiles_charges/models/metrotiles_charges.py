from odoo import models, fields, api


class Charges(models.Model):
    _name = 'metrotiles.charges'
    _description = 'Metrotiles Charges'

    name = fields.Char(string="Name")
    charge_id = fields.Many2one('metrotiles.name_charges', string="Charges and Fees")

    currency_id = fields.Many2one('res.currency', string='Currency')
    charge_amount = fields.Monetary(string="Amount", currency_field="currency_id",
                                    store=True)
    charge_sale_id = fields.Many2one(string="sale charges", comodel_name='sale.order')
    code_id = fields.Many2one('account.account', related="charge_id.account_charge_id", readonly=True)
    code_status = fields.Char(string="Status", compute="validate_code_id", readonly=True, store=False)

    @api.depends('code_id')
    def validate_code_id(self):
        if not self.code_id:
            self.update({
                'code_status': 'Charge ID needs accounting code'
            })
        else:
            self.update({
                'code_status': 'Charge code completed'
            })
