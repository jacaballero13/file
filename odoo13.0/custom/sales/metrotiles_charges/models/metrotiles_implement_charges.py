from odoo import models, api, fields


class ImplementCharges(models.Model):
    _inherit = 'sale.order'

    charge_ids = fields.One2many(string="Charges", comodel_name='metrotiles.charges',
                                 inverse_name='charge_sale_id', copy=True)
    charge_currency_id = fields.Many2one('res.currency', string='Currency')
    net_charges = fields.Monetary(string="Net Charges", currency_field="charge_currency_id",
                                  store=True, readonly=True, compute='get_net_charges')
    total_charges = fields.Monetary(string="Charges Total", currency_field="charge_currency_id",
                                    store=True, readonly=True, compute='get_total_charges')
    vat_activated = fields.Boolean(default=False)
    vat_charges = fields.Monetary(string='VAT', store=True, compute='calculate_tax_charge')

    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='calculate_amount_total',
                                   tracking=4)

    @api.depends('vat_activated', 'total_charges')
    def calculate_tax_charge(self):
        for rec in self:
            params = self.env['ir.config_parameter'].sudo()
            vat_amount = float(params.get_param('vat_amount', default=0.0))
            vat_charges = 0.0

            if rec.vat_activated:
                vat_amount = vat_amount / 100 if vat_amount > 0.0 else 0.0
                vat_charges = rec.net_charges * vat_amount

            rec.update({'vat_charges': vat_charges})

    @api.depends('charge_ids.charge_amount', 'vat_charges')
    def get_net_charges(self):
        for charges in self:
            charge_total = 0.0
            for item in charges.charge_ids:
                charge_total += item.charge_amount

            charges.update({'net_charges': charge_total})

    @api.depends('net_charges', 'vat_charges')
    def get_total_charges(self):
        for total in self:
            total.update({'total_charges': total.net_charges + total.vat_charges})

