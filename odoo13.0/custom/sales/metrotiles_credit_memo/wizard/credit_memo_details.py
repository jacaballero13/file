from odoo import api, fields, models, exceptions, SUPERUSER_ID, _


class CreditMemoDetails(models.Model):
    _name = 'credit.memo.details'
    _rec_name = 'sale_order_id'

    order_request_line = fields.One2many(
        'credit.memo.line', 'memo_id', string="Order Request Line", store=True)
    sale_order_id = fields.Many2one(
        comodel_name='sale.order', string="Sales Order", store=True, readonly=True)
    quotation_type = fields.Selection([('regular', 'Regular'), ('installation', 'Installation'), (
        'sample', 'Sample')], string="Quotation type", readonly=True)
    warehouse_id = fields.Many2one(
        comodel_name='stock.warehouse', string="warehouse", store=True, readonly=True)
    sales_ac = fields.Many2one(
        comodel_name='res.users', string="Account Coordinator", readonly=True)
    partner_id = fields.Many2one(
        comodel_name='res.partner', string="Client", readonly=True)
    select_all = fields.Boolean("Select All", default=False)
    adjustment_type = fields.Selection(
        string="Adjustment Type",
        selection=[
            ('cancel_contract', 'Cancellation of Contract'),
            ('cancel_items', 'Cancellation of Items'),
            ('change_designer', 'Change Architect & Interior Designer'),
            ('change_charges', 'Change Contract Charges'),
            ('change_items', 'Change Items'),
            ('change_discount', 'Change Discount'),
            ('change_qty', 'Change Quantity'),
            ('change_vat', 'Change VAT'),
        ])
    column_discounts = fields.Many2many('metrotiles.discount',
                                        'metrotiles_discount_column_credit_memo_rel',
                                        string="Column discounts",
                                        domain="([('discount_type','=','percentage')])",
                                        store=True,
                                        )
    total_discounts = fields.Many2many('metrotiles.discount',
                                       'metrotiles_discount_total_credit_rel',
                                       string="Discounts")

    total_amount = fields.Float(
        string="Total Amount", compute='compute_total_amount', store=True)
    vat_activated = fields.Boolean(related='sale_order_id.vatable')
    charge_vat_activated = fields.Boolean(
        related='sale_order_id.vat_activated')
    charge_vat_amount = fields.Float(
        string="Charges VAT", compute='_compute_total_charges')
    vat_amount = fields.Float(string="VAT", readonly=True)
    net_charge_amount = fields.Float(compute='_compute_total_charges')
    product_total = fields.Float(string="Product Total", readonly=True)
    charges_line_ids = fields.One2many('credit.memo.charges.line', 'memo_id')
    total_charges_amount = fields.Float(compute='_compute_total_charges')
    total_charges_product = fields.Float(compute='compute_total_amount')

    @api.depends('charges_line_ids.charge_id', 'charges_line_ids.charge_amount')
    def _compute_total_charges(self):
        total_charges = 0
        vat_amount = 0
        net_charge_amount = 0
        for rec in self.charges_line_ids:
            total_charges += rec.charge_amount
        if self.charge_vat_activated:
            vat_amount = total_charges * (12/100)
        self.net_charge_amount = total_charges
        self.charge_vat_amount = vat_amount
        self.total_charges_amount = total_charges + vat_amount

    @api.depends('order_request_line.is_select', 'order_request_line.price_subtotal_main_currency', 'total_charges_amount')
    def compute_total_amount(self):
        amount = 0
        for rec in self:
            for line in rec.order_request_line:
                if line.is_select and line.product_id:
                    amount += round(line.price_subtotal_main_currency, 2)
            if rec.vat_activated:
                rec.vat_amount = amount * (12/100)

            rec.update({'total_amount': amount,
                        'product_total': amount + rec.vat_amount,
                       'total_charges_product':  amount + rec.total_charges_amount + rec.vat_amount
                        })

    @api.onchange('select_all')
    def onchange_select(self):
        for rec in self:
            if rec.select_all:
                rec.order_request_line.update({'is_select': True})
            else:
                rec.order_request_line.update({'is_select': False})

    @api.onchange('column_discounts')
    def onchange_column_discounts(self):
        for rec in self:
            if len(rec.column_discounts) > 2:
                raise exceptions.ValidationError(
                    "Cannot add more than 2 discounts")

            for line in rec.order_request_line:
                if line.product_id.product_tmpl_id.type == 'product':
                    line.discounts = self.column_discounts

    @api.onchange('total_discounts')
    def onchange_total_discounts(self):
        for rec in self:
            if len(rec.total_discounts) > 2:
                raise exceptions.ValidationError(
                    "Cannot add more than 2 discounts")

    @api.onchange('sale_order_id')
    def onchange_request_lines(self):
        contract_line = []
        charges_line = []
        if self.sale_order_id:
            self.column_discounts = [
                rec.id for rec in self.sale_order_id.column_discounts]
            self.total_discounts = [
                rec.id for rec in self.sale_order_id.total_discounts]
            for sale_order in self.sale_order_id.order_line:
                line = (0, 0, {
                    'display_type': sale_order.display_type,
                    'sequence': sale_order.sequence,
                    'name': sale_order.name,
                    'product_id': sale_order.product_id.id,
                    'location_id': sale_order.location_id.id,
                    'application_id': sale_order.application_id.id,
                    'factory_id': sale_order.factory_id.id,
                    'series_id': sale_order.series_id.id,
                    'variant': sale_order.variant,
                    'size': sale_order.size,
                    'discounts': sale_order.discounts or [(5, 0, 0)],
                    'product_uom_qty': sale_order.product_uom_qty,
                    'price_unit_main_currency': sale_order.price_unit_main_currency,
                    'price_net_main_currency': sale_order.price_net_main_currency,
                    'price_subtotal_main_currency': sale_order.price_subtotal_main_currency})
                contract_line.append(line)
            for charges in self.sale_order_id.charge_ids:
                charges_lines = (0, 0, {
                    'charge_id': charges.charge_id.id,
                    'currency_id': charges.currency_id.id,
                    'charge_amount': charges.charge_amount,
                    'code_id': charges.code_id.id
                })
                charges_line.append(charges_lines)
            self.update({'order_request_line': contract_line,
                         'charges_line_ids': charges_line})

    @api.model
    def default_get(self, default_fields):
        res = super(CreditMemoDetails, self).default_get(default_fields)
        context = self._context
        dr_request = {
            'sale_order_id': context.get('sale_order_id'),
            'quotation_type': context.get('quotation_type'),
            'warehouse_id': context.get('warehouse_id'),
            'partner_id': context.get('partner_id'),
            'sales_ac': context.get('sales_ac'),
        }
        res.update(dr_request)
        return res

    def create_credit_memo_request(self):
        lines = []
        for rec in self:
            order = rec.sale_order_id
            for each in rec.order_request_line:
                if each.is_select:
                    lines.append((0, 0, {
                        'display_type': each.display_type,
                        'sequence': each.sequence,
                        'name': each.name,
                        'location_id': each.location_id.id,
                        'application_id': each.application_id.id,
                        'factory_id': each.factory_id.id,
                        'series_id': each.series_id.id,
                        'product_id': each.product_id,
                        'quantity': each.product_uom_qty,
                        'price_gross': each.price_unit_main_currency,
                        'discounts': each.discounts or [(5, 0, 0)],
                        'price_unit': each.price_net_main_currency,
                        'price_subtotal': each.price_subtotal_main_currency,
                    }))
            if rec.vat_activated:
                lines.append((0, 0, {
                    'display_type': None,
                    'name': "Output Vat (12.00%)",
                    'account_id': 14,
                    'exclude_from_invoice_tab': True,
                    'quantity': 1,
                    'credit': rec.vat_amount,
                    'debit': 0.0,
                    'balance': rec.vat_amount * -1,
                    'price_unit': rec.vat_amount,

                }))
            if rec.charge_vat_activated:
                lines.append((0, 0, {
                    'display_type': None,
                    'name': "Charge Vat (12.00%)",
                    'account_id': 14,
                    'exclude_from_invoice_tab': True,
                    'quantity': 1,
                    'credit': rec.charge_vat_amount,
                    'debit': 0.0,
                    'balance':  rec.charge_vat_amount * -1,
                    'price_unit': rec.charge_vat_amount,

                }))

            if len(rec.charges_line_ids) > 0:
                for charges in rec.charges_line_ids:
                    lines.append((0, 0, {
                        'display_type': None,
                        'name': charges.charge_id.name,
                        'account_id': charges.code_id.id,
                        'exclude_from_invoice_tab': True,
                        'quantity': 1,
                        'credit': charges.charge_amount,
                        'debit': 0.0,
                        'balance':  charges.charge_amount * -1,
                        'price_unit': charges.charge_amount,
                    }))

            self.env['account.move'].create({
                'ref': rec.sale_order_id.name,
                'sale_order': rec.sale_order_id.id,
                'partner_id': rec.partner_id.id,
                'invoice_payment_term_id': order.payment_term_id.id,
                'branch_id': order.branch_id.id,
                'type': 'out_refund',
                'invoice_line_ids': lines,
                'state': 'waiting',
                'vatable': rec.vat_amount,
                'net_charges': rec.net_charge_amount,
                'total_charges': rec.total_charges_amount,
                'vat_charges': rec.charge_vat_amount,
            })


class CreditMemoLine(models.Model):
    _name = 'credit.memo.line'

    memo_id = fields.Many2one('credit.memo.details',
                              readonly="True", string="Delivery Request Item")
    name = fields.Char(string="Location")
    display_type = fields.Char('Display Type')
    sequence = fields.Char('Sequence')

    is_select = fields.Boolean("Select")
    product_id = fields.Many2one(
        comodel_name='product.product', string="Description", store=True)

    location_id = fields.Many2one(
        comodel_name='metrotiles.location', string="Location", store=True)
    application_id = fields.Many2one(
        comodel_name='metrotiles.application', string="Application", store=True)

    factory_id = fields.Many2one(
        comodel_name='res.partner', string='Factory', store=True)
    series_id = fields.Many2one(
        comodel_name='metrotiles.series', string='Series', readonly=False, store=True)

    variant = fields.Char(string="Variant")
    size = fields.Char(string="Sizes (cm)")
    price_unit_main_currency = fields.Float("Gross Price")
    price_net_main_currency = fields.Float(
        "Price Net", compute='_get_net_price', store=True)
    price_subtotal_main_currency = fields.Float(
        "Amount", compute='_compute_amount', store=True)
    product_uom_qty = fields.Integer(string="Contract Qty", default=None)
    discounts = fields.Many2many('metrotiles.discount', 'metrotiles_discount_credit_memo_line_rel',
                                 string="Discounts",
                                 domain="([('discount_type','=','percentage',)])")

    @api.depends('product_id', 'product_uom_qty', 'price_unit_main_currency', 'discounts')
    def _get_net_price(self):
        for line in self:
            total_net = line.price_unit_main_currency
            for discount in line.discounts:
                if discount.discount_type == 'percentage':
                    total_net = total_net - \
                        (total_net * (discount.value / 100))
                else:
                    total_net -= discount.value

            line.update({
                'price_net_main_currency': total_net,
            })

    @api.depends('product_id', 'product_uom_qty', 'discounts', 'price_net_main_currency')
    def _compute_amount(self):
        for rec in self:
            amount = rec.product_uom_qty * rec.price_net_main_currency
            rec.update({'price_subtotal_main_currency': amount})


class CreditMemoChargesLine(models.Model):
    _name = 'credit.memo.charges.line'

    memo_id = fields.Many2one('credit.memo.details', readonly="True")
    charge_id = fields.Many2one('metrotiles.name_charges')
    currency_id = fields.Many2one('res.currency', string='Currency')
    charge_amount = fields.Monetary(string="Amount", currency_field="currency_id",
                                    store=True)
    code_id = fields.Many2one(
        'account.account', related="charge_id.account_charge_id", readonly=True)
