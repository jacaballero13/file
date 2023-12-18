# -*- coding: utf-8 -*-
from odoo import models, fields,SUPERUSER_ID, api, _
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, float_compare


class Respartner(models.Model):
    _inherit="res.partner"
    
    customer_tax_ids = fields.Many2many('account.tax', string='Customer Taxes')
    vendor_tax_ids = fields.Many2many('account.tax', string='Vendor Taxes')
    customer_wt_tax_id = fields.Many2one('account.tax', string='Withholding Tax Rate')
    vendor_wt_tax_id = fields.Many2one('account.tax', string='Withholding Tax Rate')
    
class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    @api.onchange('partner_id')
    def onchange_so_partner_id(self):
        for line in self.order_line:
            if line.product_id:
                # Compute VAT in Sale Order  based on VAT rate assigned in Partner’s Master Data
                line._compute_tax_id()

class saleorderline(models.Model):
    _inherit = "sale.order.line"
    
    
    def _compute_tax_id(self):
        for line in self:
            fpos = line.order_id.fiscal_position_id or line.order_id.partner_id.property_account_position_id
            # If company_id is set, always filter taxes by the company
            taxes = line.product_id.taxes_id.filtered(lambda r: not line.company_id or r.company_id == line.company_id)
            # Compute VAT in Sale Order  based on VAT rate assigned in Partner’s Master Data
            if (line.order_id.partner_id.customer_tax_ids):
                taxes += line.order_id.partner_id.customer_tax_ids
            line.tax_id = fpos.map_tax(taxes, line.product_id, line.order_id.partner_shipping_id) if fpos else taxes
            
class PurchaseOrder(models.Model):
    _inherit="purchase.order"
     
    @api.onchange('partner_id')
    def onchange_po_partner_id(self):
        for line in self.order_line:
            if line.product_id:
                # Compute VAT in Purchase Order  based on VAT rate assigned in Partner’s Master Data
                line.onchange_product_id()
                
                
class purchaseorderline(models.Model):
    _inherit = "purchase.order.line"
            
    @api.onchange('product_id')
    def onchange_product_id(self):
        result = {}
        if not self.product_id:
            return result
        # Reset date, price and quantity since _onchange_quantity will provide default values
        self.date_planned = datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        self.price_unit = self.product_qty = 0.0
        self.product_uom = self.product_id.uom_po_id or self.product_id.uom_id
        result['domain'] = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}

        product_lang = self.product_id.with_context(
            lang=self.partner_id.lang,
            partner_id=self.partner_id.id,
        )
        self.name = product_lang.display_name
        if product_lang.description_purchase:
            self.name += '\n' + product_lang.description_purchase

        fpos = self.order_id.fiscal_position_id
        if self.env.uid == SUPERUSER_ID:
            company_id = self.env.user.company_id.id
            taxes = self.product_id.supplier_taxes_id.filtered(lambda r: r.company_id.id == company_id)
            # Compute VAT in Purchase Order  based on VAT rate assigned in Partner’s Master Data
            if (self.order_id.partner_id.vendor_tax_ids):
                taxes += self.order_id.partner_id.vendor_tax_ids
            self.taxes_id = fpos.map_tax(taxes)
        else:
            taxes = self.product_id.supplier_taxes_id
            if (self.order_id.partner_id.vendor_tax_ids):
                taxes += self.order_id.partner_id.vendor_tax_ids
            self.taxes_id = fpos.map_tax(taxes)

        self._suggest_quantity()
        self._onchange_quantity()
        return result
    
class AccountInvoice(models.Model):
    _inherit = "account.move"
          
    @api.onchange('partner_id')
    def onchange_invoice_partner_id(self):
        for line in self.invoice_line_ids:
            if line.product_id:
                #Compute VAT in Customer Invoices and Vendor Bills based on VAT rate assigned in Partner’s Master Data
                line._set_taxes()
                
                
class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    
    def _set_taxes(self):
        """ Used in on_change to set taxes and price."""
        if self.invoice_id.type in ('out_invoice', 'out_refund'):
            taxes = self.product_id.taxes_id or self.account_id.tax_ids
            #Compute VAT in Customer Invoices based on VAT rate assigned in Partner’s Master Data 
            if (self.invoice_id.partner_id.customer_tax_ids):
                taxes += self.invoice_id.partner_id.customer_tax_ids
        else:
            taxes = self.product_id.supplier_taxes_id or self.account_id.tax_ids
            #Compute VAT in Vendor Bills based on VAT rate assigned in Partner’s Master Data 
            if (self.invoice_id.partner_id.vendor_tax_ids):
                taxes += self.invoice_id.partner_id.vendor_tax_ids

        # Keep only taxes of the company
        company_id = self.company_id or self.env.user.company_id
        taxes = taxes.filtered(lambda r: r.company_id == company_id)

        self.invoice_line_tax_ids = fp_taxes = self.invoice_id.fiscal_position_id.map_tax(taxes, self.product_id, self.invoice_id.partner_id)

        fix_price = self.env['account.tax']._fix_tax_included_price
        if self.invoice_id.type in ('in_invoice', 'in_refund'):
            prec = self.env['decimal.precision'].precision_get('Product Price')
            if not self.price_unit or float_compare(self.price_unit, self.product_id.standard_price, precision_digits=prec) == 0:
                self.price_unit = fix_price(self.product_id.standard_price, taxes, fp_taxes)
                self._set_currency()
        else:
            self.price_unit = fix_price(self.product_id.lst_price, taxes, fp_taxes)
            self._set_currency()
    
class AccountInvoiceReport(models.Model):
    _inherit = 'account.invoice.report'
    
    ref = fields.Char('Test')

    def _select(self):
        return super(AccountInvoiceReport, self)._select() + ", line.ref as ref"
