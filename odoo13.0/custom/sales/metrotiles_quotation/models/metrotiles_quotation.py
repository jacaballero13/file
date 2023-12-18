# Metrotiles Quotation
#
# This model will inherit sale order line to included the new fields and reconstruct the whole sale order
# to include the following fields that will be use in metrotiles sales quotation:
#       - Location
#       - Application
#       - Factory
#       - Series
#       - remarks
#       - Net Price
#
# Override fields
#       - price_unit to price_gross (title only to avoid revision of impacted functions)
from functools import partial

from odoo import models, fields, api, _
from odoo.tools.misc import get_lang
import re

from odoo.tools import formatLang


class Quotation(models.Model):
    _inherit = ['sale.order.line']

    location_id = fields.Many2one('metrotiles.location', string="Location", store=True)
    application_id = fields.Many2one('metrotiles.application', string="Application", store=True)
    price_unit = fields.Float('Gross Price', digits='Product Price', default=0.0)
    price_net = fields.Float(compute='_get_net_price', string="Net Price", readonly=True)

    factory_id = fields.Many2one('res.partner', string='Factory', store=True)
    series_id = fields.Many2one('metrotiles.series', string='Series', readonly=False, store=True)

    section_line = fields.Char(compute='get_line_section', store=False)
    name = fields.Text(string='Description', required=False)
    variant = fields.Char(string="Variant", compute="get_variant_from_product")
    size = fields.Char(string="Sizes (cm)", compute="get_variant_from_product")
    series_ids = fields.Binary(string='Series', default=[], store=False)

    product_uom_qty = fields.Integer(string='Quantity',required=True, default=1, track_visibility='onchange')
    # Converted value
    price_unit_main_currency = fields.Float(compute='_converted_price_unit', string='Gross Price', digits='Product Price', default=0.0)
    price_net_main_currency = fields.Float(compute='_converted_price_net', string='Price Net',
                                            digits='Product Price', default=0.0)
    price_subtotal_main_currency = fields.Float(compute='_converted_price_subtotal', string="Amount", readonly=True, store=False, track_visibility='onchange')
    
    # added field remarks   
    remarks = fields.Selection([
                                ('sale', 'Sale'),
                                ('discontinue', 'Discontinued'),
                                ], string="Remarks", readonly=True, store=True)

    #modify discontinue or on sale in odre line items
    @api.onchange('product_id')
    def get_product_status(self):
        for field in self:
            for product in field.product_id:
                if product:
                    status = product.remarks or ""
                field.update({
                    'remarks': status
                })

    def convertCurrency(self, value=0.0):
        company_currency_id = self.env.company.currency_id
        if company_currency_id.id == self.order_id.currency_id.id:
            return value
        else:
            return company_currency_id.with_context(date=self.order_id.create_date).compute(value, self.order_id.currency_id)

    @api.depends('price_unit')
    def _converted_price_unit(self):
        for field in self:
            field.price_unit_main_currency = field.convertCurrency(field.price_unit)

    @api.depends('price_net')
    def _converted_price_net(self):
        for field in self:
            field.price_net_main_currency = field.convertCurrency(field.price_net)

    @api.depends('price_subtotal')
    def _converted_price_subtotal(self):
        for field in self:
            field.price_subtotal_main_currency = field.convertCurrency(field.price_subtotal)
    
    @api.onchange('factory_id')
    def factory_onchange(self):
        for field in self:
            field.update({'series_id': None})

            ids = []

            for product in self.env['product.product'].sudo().read_group(
                    [('product_tmpl_id.seller_ids.name.id', '=', field.factory_id.id), ('series_id.id', '!=', False)],
                    fields=['series_id'], groupby=['series_id']):
                ids.append(product.get('series_id', [])[0])

            field.series_ids = ids

    @api.onchange('series_id')
    def series_onchange(self):
        for field in self:
            field.update({'product_id': None})

    @api.depends('product_id')
    def get_variant_from_product(self):
        for rec in self:
            variant = 'N/A'
            size = 'N/A'

            for attr in rec.product_id.product_template_attribute_value_ids:
                if attr.attribute_id.name == 'Variants':
                    variant = attr.name
                elif attr.attribute_id.name == 'Sizes':
                    size = attr.name

            rec.update({'variant': variant, 'size': size})

    @api.depends('name', 'display_type')
    def get_line_section(self):
        for line in self:
            str_section = re.sub("(^.*\.\s)", "", line.name, 1)

            line.update({
                'section_line': str_section,
            })

    @api.depends('product_id', 'price_net')
    def _get_net_price(self):
        total_net = 0.0
        for line in self:
            total_net = line.price_unit * (1 - line.discount / 100)

            line.update({
                'price_net': total_net,
            })

    @api.depends('product_uom_qty', 'discount', 'price_net', 'price_net', 'tax_id')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty,
                                            product=line.product_id, partner=line.order_id.partner_shipping_id)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': line.product_uom_qty * line.price_net,
            })

    def _prepare_invoice_line(self):
        """
        Prepare the dict of values to create the new invoice line for a sales order line.

        :param qty: float quantity to invoice
        """
        self.ensure_one()
        res = {
            'display_type': self.display_type,
            'sequence': self.sequence,
            'name': self.name,
            'product_id': self.product_id.id,
            'factory_id': self.factory_id.id,
            'series_id': self.series_id.id,
            'product_uom_id': self.product_uom.id,
            'quantity': self.qty_to_invoice,
            'discount': self.discount,
            'price_gross': self.price_unit,
            'price_unit': self.price_net,
            'location_id': self.location_id.id,
            'application_id': self.application_id.id,
            'price_net': self.price_net,
            # 'tax_ids': [(6, 0, self.tax_id.ids)],
            'analytic_account_id': self.order_id.analytic_account_id.id,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
            'sale_line_ids': [(4, self.id)],
        }
        if self.display_type:
            res['account_id'] = False
        return res

    @api.onchange('product_id')
    def product_change(self):
        if self.product_id.product_tmpl_id.type == 'installation':
            application_exist = self.env['metrotiles.application'].search(
                [('name', 'ilike', self.product_id.product_tmpl_id.name)], limit=1)
            if application_exist.name:
                self.application_id = application_exist
            else:
                self.application_id = self.env['metrotiles.application'].create(
                    {'name': self.product_id.product_tmpl_id.name})
