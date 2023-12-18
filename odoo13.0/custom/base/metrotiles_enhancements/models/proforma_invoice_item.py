from odoo import models, fields, api

class MetrotilesProcurementProformInvoice(models.Model):
    _inherit = 'metrotiles_procurement.proforma_invoice'

    date_availiability = fields.Date(string='Date Availiability')

class MetrotilesProcurementProformInvoice_item(models.Model):
    _inherit = 'metrotiles_procurement.proforma_invoice_item'

    factory = fields.Many2one(comodel_name="res.partner", string="Factory", readonly=False, store=True, compute="get_factory")
    weight = fields.Float(string='Weight(kg)',required=True,tracking=True, related="proforma_invoice_id.weight")
    number_of_space = fields.Float(required=True,tracking=True, related="proforma_invoice_id.number_of_space")
    payment_term_id = fields.Many2one(comodel_name='account.payment.term', string='Payment Terms', required=True, related="proforma_invoice_id.payment_term_id")


    @api.onchange('order_line')
    def get_factory(self):
        variant = 'N/A'
        size = 'N/A'
        self.partner_id = ''
        for rec in self:
            if rec.order_line:
                for order_lines in rec.order_line:
                    for products in order_lines.product_id:
                        if products.variant_seller_ids:
                            rec.partner_id = products.variant_seller_ids[0].name
                        else:
                            self.partner_id = ''
    po_date = fields.Datetime(string="PO Date", compute='_get_po_date')
    or_date_approved = fields.Datetime(string="Order Date", compute='get_contract_date')
    date_availiability = fields.Date(string="Date Availiability", related='proforma_invoice_id.date_availiability')
    availability = fields.Selection(selection=[
            ('available', "Available"),
                ('unavailable', "Unavailable")], string="Availability", related='proforma_invoice_id.availability')
    
    qty_sqm = fields.Float(string='Qty in SQM', related='order_line.qty_sqm')
    item_sqm = fields.Float(string="Item in SQM", compute="compute_item_per_sqm")
    
    price_type = fields.Selection(selection=[('per_piece', 'Piece'),
                                        ('per_sqm', 'SQM')], related='order_line.price_type', string='Price Type',default='per_piece')
    def _default_country_id(self):
        return self.env['res.currency'].search([('id', '=', '36')]).id
    
    price_amount = fields.Monetary(string="Amount", compute="compute_price_subtotal", currency_field="currency_id", store=True)
    forex_rate = fields.Float(related='apv_reference.currency_rate',  string="Forex Rate", required=True)
    php_amount = fields.Monetary("Amount/Sqm", currency_field="default_currency_id", compute="compute_conversion_amount")
    
    buy_unit_price_sqm = fields.Monetary("Buying UP/Sqm", currency_field="default_currency_id", compute="compute_buy_up_sqm")
    expense_unit_price_sql = fields.Monetary("Expense UP/Sqm", currency_field="default_currency_id",)
    
    landed_cost_sqm = fields.Monetary("LC/Sqm", currency_field="default_currency_id", compute="compute_landed_cost")
    landed_cost_pc = fields.Monetary("LC/PC", currency_field="default_currency_id", compute="compute_landed_cost")
    landed_cost_tot_sqm = fields.Monetary("LC Total Qty Sqm", currency_field="default_currency_id", compute="compute_landed_cost_total")
    landed_cost_tot_pc = fields.Monetary("LC Total Qty PC", currency_field="default_currency_id", compute="compute_landed_cost_total")
    
    apv_reference = fields.Many2one('account.move', string="Bills", compute="get_invoice_origin")
    
    currency_id = fields.Many2one('res.currency',string='Currency', related='order_line.currency_id')
    default_currency_id = fields.Many2one('res.currency',string='Currency', default=_default_country_id, readonly=True)
    
    @api.depends('po_reference')
    def get_invoice_origin(self):
        for rec in self:
            rec.apv_reference = None
            move = self.env['account.move'].search([('invoice_origin', '=', rec.po_reference ), ('type', '=', 'in_invoice')],limit=1)
            if move.state == 'posted':
                rec.apv_reference = move.id
            else:
                rec.apv_reference = None
            
    @api.depends('order_line')
    def compute_item_per_sqm(self):
        for rec in self:
            raw_cut_size = "00x00"
            raw_cut_width = 0.00
            raw_cut_length = 0.00
            for line in rec.order_line:
                for attr in line.product_id.product_template_attribute_value_ids:
                    if attr.attribute_id.name == 'Sizes':
                        raw_cut_size = attr.name
                        rcut_size = raw_cut_size.split("x")
                        raw_cut_width = rcut_size[0]
                        raw_cut_length = rcut_size[1]
            rec.item_sqm = (float(raw_cut_width) / 100) * (float(raw_cut_length) / 100)
    
    @api.depends('landed_cost_sqm', 'landed_cost_pc', 'qty_sqm', 'total_po_qty')
    def compute_landed_cost_total(self):
        for rec in self:
            rec.landed_cost_tot_sqm = (rec.landed_cost_sqm * rec.qty_sqm)
            rec.landed_cost_tot_pc = (rec.landed_cost_pc * rec.total_po_qty)

    @api.depends('buy_unit_price_sqm', 'expense_unit_price_sql', 'item_sqm')
    def compute_landed_cost(self):
        for rec in self:
            rec.landed_cost_sqm = rec.buy_unit_price_sqm + rec.expense_unit_price_sql
            rec.landed_cost_pc = (rec.landed_cost_sqm * rec.item_sqm)
    
    @api.depends('price_amount', 'forex_rate', 'qty_sqm')
    def compute_conversion_amount(self):
        for rec in self:
            rec.php_amount = (rec.forex_rate * rec.price_amount ) if rec.currency_id.name != "PHP" else rec.price_amount

    @api.depends('php_amount', 'qty_sqm')
    def compute_buy_up_sqm(self):
        for rec in self:
            if rec.php_amount > 0 and rec.qty_sqm > 0:
                rec.buy_unit_price_sqm = (rec.php_amount / rec.qty_sqm)
            else:
                rec.buy_unit_price_sqm = 0.00
            
    @api.depends('qty_sqm', 'price_unit')
    def compute_price_subtotal(self):
        for rec in self:
            rec.price_amount = (rec.price_unit * rec.qty_sqm)
    
    def _get_po_date(self):
        for rec in self:
            for items in rec.proforma_invoice_id:
                rec.po_date = items.purchase_order_id.date_approve

    def get_contract_date(self):
        for rec in self:
            sale_order = self.env['sale.order'].search([('name','=', rec.so_contract_ref.name)])
            rec.or_date_approved = sale_order.date_approved