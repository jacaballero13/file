from datetime import datetime, timedelta
from functools import partial
from itertools import groupby

from odoo import api, fields, models, SUPERUSER_ID, _, exceptions
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import formatLang, get_lang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare

# This module is for proforma invoice in procurement module

class ProformaInvoice(models.Model):
    _name = 'metrotiles_procurement.proforma_invoice'
    _description = "Purchase Proforma Invoice"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _inherits = {
        'purchase.order': 'purchase_order_id',
    }

    purchase_order_id = fields.Many2one(
        string="Purchase Order",
        comodel_name='purchase.order',
        ondelete='cascade',
        required=True,tracking=True,
        domain="[('status', '=', 'pending')]"
    )
    partner_id = fields.Many2one(string="Vendor", comodel_name='res.partner', tracking=True)

    name = fields.Char(string='Proforma Invoice No.', required=True, tracking=True)

    status = fields.Selection(selection=[
        ('cancelled', "Cancelled"),
        ('rejected', "Rejected"),
        ('pending', "Pending"),
        ('processing', "Processing"),
        ('approved', "Approved")
    ], default='pending', required=True)

    payment_status = fields.Selection(selection=[
        ('paid', "Paid"),
        ('unpaid', "Unpaid")
    ], default='paid', tracking=True)

    payment_term_id = fields.Many2one(comodel_name='account.payment.term', string='Payment Terms', required=True)

    availability = fields.Selection(selection=[
        ('available', "Available"),
        ('unavailable', "Unavailable")
    ], default='available', required=True, tracking=True)

    date_availiability = fields.Date(string='Date Availiability', default=fields.Date.today())

    number_of_space = fields.Float(required=True,tracking=True)

    weight = fields.Float(string='Weight(kg)',required=True,tracking=True)

    currency = fields.Many2one(comodel_name='res.currency', tracking=True)

    proforma_item_ids = fields.One2many(comodel_name='metrotiles_procurement.proforma_invoice_item', inverse_name='proforma_invoice_id')

    amount_total = fields.Monetary(string='Grand Total', compute='get_amount_total', default=0,)
    
    proforma_attach = fields.Binary(string="Add Attachment")

    @api.depends('proforma_item_ids.price_subtotal')
    def get_amount_total(self):
        for proforma in self:
            total_amount = 0
            for item in proforma.proforma_item_ids:
                total_amount += item.price_subtotal
            proforma.amount_total = proforma.purchase_order_id.amount_total

    def action_rejected(self):
        self.status = 'rejected'

    def action_cancelled(self):
        self.status = 'rejected'

    def action_pending(self):
        self.status = 'pending'

    def action_processing(self):
        self.status = 'processing'

    def action_approved(self):
        for proforma in self:
            total_proforma_items = 0
            total_purchase_items = 0
            purchase_items = self.env['purchase.order.line'].search(args=[
                ('order_id', '=', proforma.purchase_order_id.id)
            ])
            proforma_records = self.env['metrotiles_procurement.proforma_invoice'].search(args=[
                ('purchase_order_id', '=', proforma.purchase_order_id.id),
                ('status', '=', 'approved')
            ])
            for item in proforma.proforma_item_ids:
                total_proforma_items += item.product_qty
            # lineup_object = self.env['proforma_invoice.lineup']
            # proforma_lineup_shipments = ({
            #         'proforma_invoice_id': self.id, 
            #         'order_line': purchase_items.product_id.id,
            #         'proforma_item_ids': self.id,
            #     })
            # proforma_line = lineup_object.create(proforma_lineup_shipments)
            # print(proforma_line)
            if len(proforma_records):
                for proforma_record in proforma_records:
                    for item in proforma_record.proforma_item_ids:
                        total_proforma_items += item.product_qty

            if len(purchase_items):
                for item in purchase_items:
                    total_purchase_items += item.product_qty
            remaining_items = total_purchase_items - total_proforma_items
            if remaining_items < 0:
                pass
                # raise exceptions.ValidationError("The Item that you requested is more than the remaining amount!")

            elif remaining_items == 0:
                proforma.purchase_order_id.update({
                    'status': 'completed'
                })
                proforma.status = 'approved'
                if proforma.payment_status == 'unpaid':
                    proforma.env['metrotiles_procurement.accounting_proforma_invoice'].create({
                        'purchase_proforma_invoice_id': self.id
                    })

            else:
                proforma.status = 'approved'
                if proforma.payment_status == 'unpaid':
                    proforma.env['metrotiles_procurement.accounting_proforma_invoice'].create({
                        'purchase_proforma_invoice_id': self.id
                    })

            for item in proforma.proforma_item_ids:
                item.order_line.update({
                    'remaining_qty': item.order_line.remaining_qty - item.product_qty
                })
            #added this line for the meantime
            proforma.status = 'approved'
            proforma.purchase_order_id.update({
                'status': 'completed'
            })
            
