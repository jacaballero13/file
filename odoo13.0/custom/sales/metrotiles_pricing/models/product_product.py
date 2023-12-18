from odoo import models, fields, api, exceptions
from odoo.exceptions import UserError

class ProductTemplate(models.Model):
    _inherit = "product.template"
    
    
    # price_type = fields.Selection(selection=[('net', 'NET'),
    #                             ('gross', 'Gross')])

    def metrotiles_calculate_price(self, price, seller_currency, date):
        company_currency_id = self.env.company.currency_id

        if company_currency_id.id == seller_currency.id:
            return price
        else:
            return company_currency_id.with_context(date=date).compute(price,seller_currency)
    """ 
        Temporary comment this line when duplicating products
    """
    # def calculate_price_by_vendor(self, val):
    #     # if len(val['seller_ids'][0][1]):
    #     if len(self.seller_ids) > 0:
    #         seller = val['seller_ids'][0][2]
    #         price = seller['price']
    #         seller_currency = self.env['res.currency'].search([('id', '=', seller['currency_id'])])

    #         val['list_price'] = self.metrotiles_calculate_price(price, seller_currency, date=fields.Date.today())


    def update_price_write(self, vals):
        sellers = vals.get('seller_ids', False)
        list_price = vals.get('list_price')

        if list_price or sellers:
            if sellers:
                writeType = sellers[0][0]
                seller_data = sellers[0][2]

                if writeType == 1:
                    seller = self.env['product.supplierinfo'].sudo().search([('id', '=', sellers[0][1])])

                    seller_price = seller.price
                    seller_currency = seller.currency_id

                    if seller_data.get('price'):
                        seller_price = seller_data.get('price')

                    if seller_data.get('currency_id'):
                        currency = self.env['res.currency'].sudo().search([('id', '=', seller_data.get('currency_id'))])
                        seller_currency = currency

                    vals['list_price'] = self.metrotiles_calculate_price(seller_price, seller_currency,
                                                    fields.Date.today())
                    print('updated')
                elif writeType == 2: # removed
                    vals['list_price'] = 1
                elif writeType == 0: # created
                    print('created')
                    currency = self.env['res.currency'].sudo().search([('id', '=', seller_data['currency_id'])])
                    vals['list_price'] = self.metrotiles_calculate_price(seller_data['price'], currency,
                                                    fields.Date.today())

    @api.model_create_multi
    def create(self, vals_list):
        ''' Store the initial standard price in order to be able to retrieve the cost of a product template for a given date'''
        # for val in vals_list:
        #     # self.calculate_price_by_vendor(val)
        templates = super(ProductTemplate, self).create(vals_list)
        if "create_product_product" not in self._context:
            templates._create_variant_ids()

        # This is needed to set given values to first variant after creation
        for template, vals in zip(templates, vals_list):
            related_vals = {}
            if vals.get('barcode'):
                related_vals['barcode'] = vals['barcode']
            if vals.get('default_code'):
                related_vals['default_code'] = vals['default_code']
            if vals.get('standard_price'):
                related_vals['standard_price'] = vals['standard_price']
            if vals.get('volume'):
                related_vals['volume'] = vals['volume']
            if vals.get('weight'):
                related_vals['weight'] = vals['weight']
            # Please do forward port
            if vals.get('packaging_ids'):
                related_vals['packaging_ids'] = vals['packaging_ids']
            if related_vals:
                template.write(related_vals)

        return templates

    def write(self, vals):
        self.update_price_write(vals)
        res = super(ProductTemplate, self).write(vals)
        # self.update_price_write()

        if 'attribute_line_ids' in vals or vals.get('active'):
            self._create_variant_ids()
        if 'active' in vals and not vals.get('active'):
            self.with_context(active_test=False).mapped('product_variant_ids').write({'active': vals.get('active')})
        if 'image_1920' in vals:
            self.env['product.product'].invalidate_cache(fnames=[
                'image_1920',
                'image_1024',
                'image_512',
                'image_256',
                'image_128',
                'can_image_1024_be_zoomed',
            ])
        return res


class ProductProduct(models.Model):
    _inherit = "product.product"

    pricing_type = fields.Selection(selection=[('net', 'NET'),
                                ('gross', 'Gross')])
    
    # @api.depends('list_price', 'price_extra')
    # @api.depends_context('uom')
    # def _compute_product_lst_price(self):
    #     to_uom = None
    #     if 'uom' in self._context:
    #         to_uom = self.env['uom.uom'].browse(self._context['uom'])

    #     for product in self:
    #         if to_uom:
    #             list_price = product.uom_id._compute_price(product.list_price, to_uom)
    #         else:
    #             list_price = product.list_price
    #         product.lst_price = list_price + product.price_extra

    #     print('how are you')

    def _set_product_price(self):
        for product in self:
            if self._context.get('uom'):
                value = self.env['uom.uom'].browse(self._context['uom'])._compute_price(product.price, product.uom_id)
            else:
                value = product.price
            value -= product.price_extra
            product.write({'list_price': value})

        print('_set_product_price')

    def _set_product_lst_price(self):
        for product in self:
            if self._context.get('uom'):
                value = self.env['uom.uom'].browse(self._context['uom'])._compute_price(product.lst_price,
                                                                                        product.uom_id)
            else:
                value = product.lst_price
            value -= product.price_extra
            product.write({'list_price': value})


        print('_set_product_lst_price')


    @api.depends('list_price', 'price_extra', 'pricing_type', 'seller_ids')
    @api.depends_context('uom')
    def _compute_product_lst_price(self):
        to_uom = None
        if 'uom' in self._context:
            to_uom = self.env['uom.uom'].browse(self._context['uom'])
        n_factor = 0
        ex_rate = 0
        mrgn_sqm = 0
        mgrn_pc = 0
        disc_sqm = 0
        disc_pc =0
        seller_price = 0
        price_total = 0
        for product in self:
            for sellers in self.seller_ids:
                seller = sellers.name[0].id
                seller_price = sellers.price if sellers.price > 0 else 0.00
                partner_id = self.env['res.partner'].search([('id','=', seller)], limit=1)
                for factory in partner_id.factory_settings:
                    n_factor = factory.number_factor
                    ex_rate = factory.exchange_rate
                    mrgn_sqm = factory.margin_sqm
                    mgrn_pc = factory.margin_piece
                    disc_sqm = factory.discount_sqm
                    disc_pc = factory.discount_piece
                    break
            price = product.list_price
            size = product.get_size()
            if product.pricing_type == 'net':
                if (product.uom_po_id.name.lower() == 'sqm' and size != 'N/A'):
                    price_sqm = (float(size[0]) / 100) * (float(size[1]) / 100)
                    price_total = (float(seller_price) + float(n_factor)) * ex_rate * price_sqm
                    price = ((price_total * mrgn_sqm / 100)) + price_total
                else:
                    price_pc = ((float(seller_price) + float(n_factor)) * ex_rate)
                    price = ((price_pc) * (mgrn_pc / 100)) + price_pc
            elif product.pricing_type == 'gross':
                if (product.uom_po_id.name.lower() == 'sqm' and size != 'N/A'):
                    price_sqm = (float(size[0]) / 100) * (float(size[1]) / 100)
                    disc_sqm = (seller_price - (seller_price * (disc_sqm / 100)) + n_factor) * ex_rate
                    gross_sqm = ((mrgn_sqm / 100) * disc_sqm) * price_sqm
                    price =  gross_sqm + (disc_sqm * price_sqm)
                else:
                    price_pc = (float(seller_price) - ((seller_price)*(disc_pc / 100))) + float(n_factor)
                    price_ex_rate = price_pc * ex_rate
                    price = (price_ex_rate + ((price_ex_rate)*(mgrn_pc / 100)))
            if to_uom:
                list_price = product.uom_id._compute_price(price, to_uom)
            else:
                list_price = price
            
            product.lst_price = list_price + product.price_extra
	  
	  
        
    @api.depends_context('pricelist', 'partner', 'quantity', 'uom', 'date', 'no_variant_attributes_price_extra')
    def _compute_product_price(self):
        prices = {}
        pricelist_id_or_name = self._context.get('pricelist')
        if pricelist_id_or_name:
            pricelist = None
            partner = self.env.context.get('partner', False)
            quantity = self.env.context.get('quantity', 1.0)

            # Support context pricelists specified as list, display_name or ID for compatibility
            if isinstance(pricelist_id_or_name, list):
                pricelist_id_or_name = pricelist_id_or_name[0]
            if isinstance(pricelist_id_or_name, str):
                pricelist_name_search = self.env['product.pricelist'].name_search(pricelist_id_or_name, operator='=',
                                                                                  limit=1)
                if pricelist_name_search:
                    pricelist = self.env['product.pricelist'].browse([pricelist_name_search[0][0]])
            elif isinstance(pricelist_id_or_name, int):
                pricelist = self.env['product.pricelist'].browse(pricelist_id_or_name)

            if pricelist:
                quantities = [quantity] * len(self)
                partners = [partner] * len(self)
                prices = pricelist.get_products_price(self, quantities, partners)

        for product in self:
            product.price = prices.get(product.id, 0.0)

            print(product.price)

    def get_size(self):
        size = 'N/A'

        for attr in self.product_template_attribute_value_ids:
            if attr.attribute_id.name == 'Sizes':
                size = attr.name

        if(size != 'N/A'):
            size = size.strip().lower()
            size = size.split('x')
            size = [float(size[0]), float(size[1])]

        return size

    def price_compute(self, price_type, uom=False, currency=False, company=False):
        # TDE FIXME: delegate to template or not ? fields are reencoded here ...
        # compatibility about context keys used a bit everywhere in the code
        if not uom and self._context.get('uom'):
            uom = self.env['uom.uom'].browse(self._context['uom'])
        if not currency and self._context.get('currency'):
            currency = self.env['res.currency'].browse(self._context['currency'])

        products = self
        if price_type == 'standard_price':
            # standard_price field can only be seen by users in base.group_user
            # Thus, in order to compute the sale price from the cost for users not in this group
            # We fetch the standard price as the superuser
            products = self.with_context(
                force_company=company and company.id or self._context.get('force_company', self.env.company.id)).sudo()

        prices = dict.fromkeys(self.ids, 0.0)
        for product in products:
            if product.is_product_variant:
                prices[product.id] = product.lst_price or 0.0
            else:
                prices[product.id] = product[price_type] or 0.0

            if price_type == 'list_price':
                prices[product.id] += product.price_extra
                # we need to add the price from the attributes that do not generate variants
                # (see field product.attribute create_variant)
                if self._context.get('no_variant_attributes_price_extra'):
                    # we have a list of price_extra that comes from the attribute values, we need to sum all that
                    prices[product.id] += sum(self._context.get('no_variant_attributes_price_extra'))

            if uom:
                prices[product.id] = product.uom_id._compute_price(prices[product.id], uom)

            # Convert from current user company currency to asked one
            # This is right cause a field cannot be in more than one currency
            if currency:
                prices[product.id] = product.currency_id._convert(
                    prices[product.id], currency, product.company_id, fields.Date.today())

        return prices

    @api.model_create_multi
    def create(self, vals_list):
        for val in vals_list:
            print(val)
        print(vals_list)
        products = super(ProductProduct, self.with_context(create_product_product=True)).create(vals_list)
        # `_get_variant_id_for_combination` depends on existing variants
        self.clear_caches()
        return products

