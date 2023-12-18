# Metrotiles Name Change
#
# This module will inherit product.product to modify the description name in sales order.
# This module will prevent from duplicating the names in the product_id.
from odoo import models, fields, api


class NameChangeTemplate(models.Model):
    _inherit = 'sale.order.template.line'

    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.ensure_one()
        if self.product_id:
            name = self.product_id.display_name
            if self.product_id.product_tmpl_id.name == name:
                if self.product_id.product_tmpl_id.type not in ['installation', 'material_service']:
                    name = "{} {} {}".format(self.product_id.product_tmpl_id.series_id.name, '-',
                                             self.product_id.display_name)
                # else:
                #     name = "{} {} {}".format(self.product_id.display_name, '-', self.product_id.product_tmpl_id.type)

            if self.product_id.description_sale:
                name += '\n' + self.product_id.description_sale
            self.name = name
            self.price_unit = self.product_id.lst_price
            self.product_uom_id = self.product_id.uom_id.id
