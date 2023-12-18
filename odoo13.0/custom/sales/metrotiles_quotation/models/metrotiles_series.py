# Metrotiles Series model
#
# This model will create a new field called Series. This new field will determine what particular series in a factory
# of a product.
from odoo import models, fields


class Series(models.Model):
    _name = 'metrotiles.series'
    _description = 'Series model'
    _sql_constraints = [ ('series_uniq',
                        'UNIQUE (name)',
                        'Series already exists'), ]


    name = fields.Char(string='Series')
    description_name = fields.Char(string='Display Name')
