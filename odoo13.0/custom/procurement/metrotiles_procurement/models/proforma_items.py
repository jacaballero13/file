from datetime import datetime, timedelta
from functools import partial
from itertools import groupby

from odoo import api, fields, models, SUPERUSER_ID, _, exceptions
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import formatLang, get_lang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare

class ProformaInvoiceItems(models.Model):
    _name = 'metrotiles_procurement.proforma_invoice_item'


    proforma_invoice_id = fields.Many2one(comodel_name='metrotiles_procurement.proforma_invoice', readonly=True, store=True,)

    # shipment_id = fields.Many2one(comodel_name="shipment.number", string="Shipment No.",readonly=True, store=True)

    bill_ids = fields.Many2one(comodel_name='shipment.lading_number', string="Bill lading")

    purchase_order_id = fields.Many2one(comodel_name='purchase.order',readonly=True, store=True)

    order_line = fields.Many2one(comodel_name='purchase.order.line', domain="[('order_id', '=', purchase_order_id)]", required=True)

    po_reference = fields.Char(string="Purchase Order", compute="get_purchase_origin", store=True)

    proforma_item_ids = fields.Many2one(comodel_name='metrotiles_procurement.proforma_invoice_item')

    total_po_qty = fields.Float(string='Contract Qty',related='order_line.product_qty', digits=(12,2))

    check_product_qty = fields.Boolean(string='Partial Quantity Order?' , default=False)

    product_qty = fields.Float(string='Supplied Qty',digits=(12,2), default=0, required=True)

    check_additional_qty = fields.Boolean(string='Add Additional Stock?', default=False)

    additional_qty = fields.Float(string='Stock Qty',default=0, digits=(12,2), required=True)

    product_uom_id = fields.Many2one(comodel_name='uom.uom', string='Unit of Measure')

    total_qty = fields.Float(compute='get_total_qty', digits=(12,2))

    price_unit = fields.Float(string='Unit Price', related='order_line.price_unit', digits='Product Price', readonly=False)

    price_subtotal = fields.Float(compute='_compute_amount', digits=(12,2), string='Subtotal', store=True)

    remaining_qty = fields.Float(compute='get_remaining_qty', digits=(12,2), store=True)

    weight = fields.Float(string='Weight(kg)',required=True,tracking=True, related="proforma_invoice_id.weight")

    status = fields.Selection(selection=[
        ('cancelled', "Cancelled"),
        ('rejected', "Rejected"),
        ('pending', "Pending"),
        ('processing', "Processing"),
        ('approved', "Approved")
    ], default='pending', required=True, related="proforma_invoice_id.status")
    
    variant = fields.Char(string="Variant", compute='get_fact_series')
    size = fields.Char(string="Sizes (cm)", compute='get_fact_series')
    
    series_id = fields.Many2one(comodel_name='metrotiles.series', string='Series', readonly=False, store=True, compute="get_fact_series")
    partner_id = fields.Many2one(comodel_name="res.partner", string="Factory", readonly=False, compute="get_fact_series")

    @api.onchange('order_line')
    def get_fact_series(self):
        variant = 'N/A'
        size = 'N/A'
        self.partner_id = ''
        for rec in self:
            if rec.order_line:
                for order_lines in rec.order_line:
                    for products in order_lines.product_id:
                        if products.variant_seller_ids:
                            rec.partner_id = products.variant_seller_ids[0].name
                        if products:
                            rec.series_id = products.series_id.id
                    for attr in order_lines.product_id.product_template_attribute_value_ids:
                        if attr.attribute_id.name == 'Variants':
                            variant = attr.name
                        elif attr.attribute_id.name == 'Sizes':
                            size = attr.name
                            
                    rec.update({'variant': variant, 'size': size})

    @api.depends('proforma_invoice_id') 
    def get_purchase_origin(self):
        for rec in self:
            for record in rec.proforma_invoice_id:
                rec.update({
                    'po_reference': record.purchase_order_id.name
                })

    @api.depends('order_line','product_qty', 'check_product_qty')
    def get_remaining_qty(self):
        for item in self:
            remaining_item = 0
            if item.check_product_qty == True:
                remaining_item = item.order_line.remaining_qty - item.product_qty
                if remaining_item < 0:
                    raise exceptions.ValidationError("Item exceed the contract remaining quantity!")
            # else:
            #     raise exceptions.ValidationError(remaining_item)
            item.remaining_qty = remaining_item

    @api.onchange('order_line', 'check_product_qty')
    def onchange_check_product_qty(self):
        for items in self:
            if len(items.purchase_order_id):
                items.product_qty = items.total_po_qty
                # if items.check_product_qty == False:
                #     items.product_qty = items.order_line.remaining_qty
                # else:
                #     items.product_qty = 0


    @api.depends('order_line','product_qty', 'additional_qty', 'check_product_qty', 'total_po_qty')
    def get_total_qty(self):
        for item in self:
            item.total_qty = item.total_po_qty
            # if item.check_product_qty == True:
            #     item.total_qty = item.product_qty + item.additional_qty
            # else:
            #     item.total_qty = item.order_line.remaining_qty + item.additional_qty



    @api.depends('order_line', 'product_qty', 'price_unit', 'additional_qty', 'check_product_qty')
    def _compute_amount(self):
        for item in self:
            if item.check_product_qty == True:
                item.price_subtotal = item.price_unit * (item.product_qty + item.additional_qty)
            else:
                item.price_subtotal = item.price_unit * (item.order_line.remaining_qty + item.additional_qty)

    # @api.onchange('product_qty')
    # def change_product_qty(self):
    #     for item in self:
    #         if len(item.order_line):
    #             if item.product_qty > item.total_po_qty:
    #                 raise exceptions.ValidationError("Item exceed the contract quantity!")

    # @api.model
    # def create(self, vals_list):
    #     proforma_items = super(ProformaInvoiceItems, self).create(vals_list)
    #     for proforma in proforma_items:
    #         check_proforma_items = self.env['metrotiles_procurement.proforma_invoice_item'].search(args=[
    #             ('proforma_invoice_id', '=', proforma.proforma_invoice_id.id),
    #             ('order_line', '=', proforma.order_line.id)
    #         ])
    #         if len(check_proforma_items) > 1:
    #             raise exceptions.ValidationError("Item already existed!")
    #     return proforma_items

