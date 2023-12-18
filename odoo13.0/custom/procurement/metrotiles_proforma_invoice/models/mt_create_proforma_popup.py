from datetime import datetime, timedelta
from odoo import api, fields, models, SUPERUSER_ID, _, exceptions
from odoo.exceptions import AccessError, UserError, ValidationError


# This module is for creating proforma invoice in purchase module
class MtCreateProformaPopup(models.Model):
    _name = 'mt_create.proforma_popup'
    _description = "Purchase Order Create Proforma Invoice"

    purchase_order_id = fields.Many2one(
        string="Purchase Order",
        comodel_name='purchase.order',
        required=True,tracking=True,
    )
    partner_id = fields.Many2one(string="Vendor", comodel_name='res.partner', related='purchase_order_id.partner_id', tracking=True)
    name = fields.Char(string='Proforma Invoice No.', required=True, tracking=True)
    status = fields.Selection(selection=[
        ('cancelled', "Cancelled"),
        ('rejected', "Rejected"),
        ('pending', "Pending"),
        ('processing', "Processing"),
        ('approved', "Approved")
    ], default='pending', required=True)
    
    payment_term_id = fields.Many2one(comodel_name='account.payment.term', string='Payment Terms', required=True)
    availability = fields.Selection(selection=[
        ('available', "Available"),
        ('unavailable', "Unavailable")
    ], default='available', required=True, tracking=True)
    date_availiability = fields.Date(string='Date Availiability', default=fields.Date.today())

    number_of_space = fields.Float(required=True,tracking=True)
    weight = fields.Float(string='Weight(kg)',required=True,tracking=True)
    currency = fields.Many2one(comodel_name='res.currency', tracking=True)
    proforma_attach = fields.Binary(string="Add Attachment")

    @api.onchange('purchase_order_id')
    def onchange_order(self):
        for rec in self:
            rec.update({
                'currency': rec.purchase_order_id.currency_id.id,
                'payment_term_id': rec.purchase_order_id.payment_term_id.id,
            })

    def action_create_proforma_invoice(self):
        proforma_obj = self.env['metrotiles_procurement.proforma_invoice']
        data = []

        for rec in self:
            for line in rec.purchase_order_id.order_line:
                data.append((0, 0, {
                    'order_line': line.id
                }))

            proforma_obj.create({
                'purchase_order_id': rec.purchase_order_id.id,
                'name': rec.name,
                'payment_term_id': rec.payment_term_id.id,
                'partner_id': rec.partner_id.id,
                'availability': rec.availability,
                'number_of_space': rec.number_of_space,
                'weight': rec.weight,
                'currency': rec.currency.id,
                'proforma_attach': rec.proforma_attach,
                'proforma_item_ids': data,
            })

            # Redirect to the newly created proforma invoice view
            # return {
            #     'name': _('Pro-Forma Invoice'),
            #     'view_mode': 'form',
            #     'res_model': 'metrotiles_procurement.proforma_invoice',
            #     'res_id': proforma.id,
            #     'type': 'ir.actions.act_window',
            #     'target': 'current',
            # }
