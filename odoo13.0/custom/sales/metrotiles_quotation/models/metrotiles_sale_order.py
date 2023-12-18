from odoo import models, fields, api


class MetrotilesSaleOrder(models.Model):
    _inherit = 'sale.order'

    need_approval = fields.Boolean(string="Need Approval", compute="sale_order_template_id_changed")
    installation_ids = fields.One2many('metrotiles.installation', 'order_id', string="Installations")
    quotation_type = fields.Selection([('regular', 'Regular'), ('installation', 'Installation')],
                                    default="regular",
                                    string="Quotation type", required=True)

    installation_total = fields.Monetary('Installation Total', compute="get_installation_total")

    is_a_version = fields.Boolean(string='Is A Version', default=False)
    latest_version = fields.Integer(string='Latest Version', default=1)

    version = fields.Integer('Version', default=1)
    root_sale_order = fields.Many2one('sale.order', string='Root Sale Order')
    source_document = fields.Char(string='Source Document')

    versions = fields.One2many('sale.order', 'root_sale_order', string="versions", domain=[('is_a_version', '=', True)],
                            order="id desc")

    @api.depends('sale_order_template_id')
    def sale_order_template_id_changed(self):
        for rec in self:
            rec.need_approval = rec.sale_order_template_id.need_approval

    @api.depends('installation_ids.subtotal')
    def get_installation_total(self):
        for rec in self:
            total = 0.0
            for installation in rec.installation_ids:
                total += installation.subtotal

            rec.update({'installation_total': total})

    def getLatestVersion(self):
        return self.versions.search([], limit=1, order='version desc')

    @api.model
    def create(self, vals):
        if vals.get('quotation_type', '') != 'installation':
            vals.pop('installation_ids') if vals.get('installation_ids', False) else None

        res = super(MetrotilesSaleOrder, self).create(vals)
        return res

    def write(self, values):
        should_create_new_version = self.check_if_to_new_version(values)

        if not self.is_a_version and self.state == 'draft' and values.get('state',
                                                                          '') != 'sale' and should_create_new_version:
            values['root_sale_order'] = self.id
            values['latest_version'] = self.latest_version + 1

            if not self.is_a_version and self.state == 'draft':
                self.copy(default={
                    'is_a_version': True,
                    'name': '{} v{}'.format(self.name, self.latest_version),
                    'version': self.latest_version,
                    'root_sale_order': self.id,
                    'source_document': self.name,
                    'currency_id': self.currency_id,
                    'state': 'cancel'
                })

        old = self
        res = super(MetrotilesSaleOrder, self).write(values)

        # if not old.is_a_version and self.state == 'draft' and should_create_new_version:
        #     cop = old.copy(default={
        #         'is_a_version': True,
        #         'name': '{} v{}'.format(old.name, self.latest_version),
        #         'version': self.latest_version,
        #         'root_sale_order': old.id,
        #         'source_document': old.name,
        #         'currency_id': old.currency_id,
        #         'state': 'cancel'
        #     })

        return res

    def check_if_to_new_version(self, values):
        check_modified = (
            'partner_id',
            'partner_invoice_id',
            'partner_shipping_id',
            'validity_date',
            'quotation_date',
            'payment_term_id',
            'order_line',
            'charge_ids',
            'quotation_type',
            'architect_ids',
            'designer_ids',
            'signed_by',
            'singed_on',
            'signature',
            'total_discounts'
        )

        should_create_new_version = False

        for field in check_modified:
            if values.get(field):
                should_create_new_version = True

                break

        return should_create_new_version

    @api.onchange('sale_order_template_id')
    def onchange_sale_order_template_id(self):
        if not self.sale_order_template_id:
            self.require_signature = self._get_default_require_signature()
            self.require_payment = self._get_default_require_payment()
            return
        template = self.sale_order_template_id.with_context(lang=self.partner_id.lang)

        order_lines = [(5, 0, 0)]
        for line in template.sale_order_template_line_ids:
            data = self._compute_line_data_for_template_change(line)
            if line.product_id:
                discount = 0
                if self.pricelist_id:
                    price = self.pricelist_id.with_context(uom=line.product_uom_id.id).get_product_price(
                        line.product_id, 1, False)
                    if self.pricelist_id.discount_policy == 'without_discount' and line.price_unit:
                        discount = (line.price_unit - price) / line.price_unit * 100
                        # negative discounts (= surcharge) are included in the display price
                        if discount < 0:
                            discount = 0
                        else:
                            price = line.price_unit
                    elif line.price_unit:
                        price = line.price_unit

                else:
                    price = line.price_unit

                data.update({
                    'location_id': line.location_id,
                    'application_id': line.application_id,
                    'factory_id': line.factory_id,
                    'series_id': line.series_id,
                    'price_unit': price,
                    'discount': 100 - ((100 - discount) * (100 - line.discount) / 100),
                    'product_uom_qty': line.product_uom_qty,
                    'product_id': line.product_id.id,
                    'product_uom': line.product_uom_id.id,
                    'customer_lead': self._get_customer_lead(line.product_id.product_tmpl_id),
                })
                if self.pricelist_id:
                    data.update(self.env['sale.order.line']._get_purchase_price(self.pricelist_id, line.product_id,
                                                                                line.product_uom_id,
                                                                                fields.Date.context_today(self)))
            order_lines.append((0, 0, data))

        self.order_line = order_lines
        self.order_line._compute_tax_id()

        option_lines = [(5, 0, 0)]
        for option in template.sale_order_template_option_ids:
            data = self._compute_option_data_for_template_change(option)
            option_lines.append((0, 0, data))
        self.sale_order_option_ids = option_lines

        if template.number_of_days > 0:
            self.validity_date = fields.Date.to_string(datetime.now() + timedelta(template.number_of_days))

        self.require_signature = template.require_signature
        self.require_payment = template.require_payment

        if template.note:
            self.note = template.note
