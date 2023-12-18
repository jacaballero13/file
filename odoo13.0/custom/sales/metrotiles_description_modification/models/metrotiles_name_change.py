# Metrotiles Name Change
#
# This module will inherit product.product to modify the description name in sales order.
# This module will prevent from duplicating the names in the product_id.
from odoo import models, fields, api


class NameChange(models.Model):
    _inherit = 'product.product'

    def get_product_multiline_description_sale(self):
        """ Compute a multiline description of this product, in the context of sales
                (do not use for purchases or other display reasons that don't intend to use "description_sale").
            It will often be used as the default description of a sale order line referencing this product.
        """
        name = self.display_name
        if self.product_tmpl_id.name == name:
            if self.product_tmpl_id.type not in ['installation', 'material_service']:
                name = "{} {} {}".format(self.product_tmpl_id.series_id.name, '-', self.display_name)
            # else:
            #     name = "{} {} {}".format(self.display_name, '-', self.product_tmpl_id.type)

        if self.description_sale:
            name += '\n' + self.description_sale

        return name
