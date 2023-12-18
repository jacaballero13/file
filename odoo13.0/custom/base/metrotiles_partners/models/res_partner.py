from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class Partner(models.Model):
    _inherit = "res.partner"

    category_id = fields.Many2many('res.partner.category', column1='partner_id',
                                   column2='category_id', string='Tags', default=lambda self: self.default_category())

    name_abbrev = fields.Char('Name Abbreviation')

    product_cat = fields.Many2one('product.category', string='product.category')

    _sql_constraints = [
        ('abbrev_unique', 'unique(name_abbrev)', 'Abbreviation already exists!')
    ]

    # total_item_purchase = fields.Float('Total Items', compute="get_total_items", store=True)

    # @api.depends('total_items_to_purchase')
    # def get_total_items(self):
    #     self.total_item_purchase = self.total_items_to_purchase

    @api.constrains('name_abbrev', 'category_id')
    def _check_abbrev(self):
        isValid = True

        if len(self.category_id) > 0:
            settings = self.sudo().env['res.config.settings'].search([])
            res_cat_vendor_tag_id = settings.res_cat_vendor_tag_id.id

            for cat in self.category_id:
                if cat.id == res_cat_vendor_tag_id:
                    isValid = self.name_abbrev is not False

                    break

        if not isValid:
            raise ValidationError(_('Vendor must have Abbreviation!'))

    def default_category(self):
        cats = []
        cats.extend(self.env['res.partner.category'].browse(self._context.get('category_id')))

        if self.env.context.get('is_creating_architect') or self.env.context.get('is_creating_interior_designer'):
            commission_type = 'architect' if self.env.context.get('is_creating_architect') else 'interior designer'
            default_category = self.env['res.partner.category'].search([('name', '=ilike', commission_type)], limit=1)

            if default_category.id:
                cats.append(default_category.id)

        elif self.env.context.get('is_creating_product_vendor') :
            default_category = self.env['res.partner.category'].search([('name', '=ilike', 'vendor')],
                                                                           limit=1)
            if default_category.id:
                cats.append(default_category.id)

        elif self.env.context.get('is_creating_customer'):
            default_category = self.env['res.partner.category'].search([('name', '=ilike', 'customer')],
                                                                           limit=1)
            if default_category.id:
                cats.append(default_category.id)

        return cats

    def create_product_category(self, val):
        settings = self.sudo().env['res.config.settings'].search([])
        base_cat = settings.base_category_id.id
        res_cat_vendor_tag_id = settings.res_cat_vendor_tag_id.id

        if val.get('category_id', False):
            for cat in val.get('category_id')[0][2]:
                if cat == res_cat_vendor_tag_id:
                    prod_cat = self.sudo().env['product.category'].create({'name': val.get('name_abbrev'), 'parent_id': base_cat})
                    val['product_cat'] = prod_cat.id

                break

    @api.model_create_multi
    def create(self, vals_list):
        for val in vals_list:
            self.create_product_category(val)

        partners = super(Partner, self).create(vals_list)

        return partners

    def write(self, vals):
        super(Partner, self).write(vals)

        if vals.get('name_abbrev'):
            self.product_cat.name = self.name_abbrev