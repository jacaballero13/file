# Metrotiles Series model
#
# This model will create a new field called Series. This new field will determine what particular series in a factory
# of a product.
from odoo import models, fields


class MetrotilesQuotationVersion(models.Model):
    _name = 'metrotiles.quotation.version'
    _inherits = {'sale.order': 'sale_order'}
    _description = 'Metrotiles Quotation Versioning'

    version = fields.Integer('Version', default=0)
    sale_order = fields.Many2one('sale.order', string='Sale Order', required=True, ondelete="cascade")
    root_sale_order = fields.Many2one('sale.order', string='Root Sale Order', required=True, ondelete="cascade")
    source_document = fields.Char(string='Source Document')

    def name_get(self):
        return [(self.id, self.sale_order)]