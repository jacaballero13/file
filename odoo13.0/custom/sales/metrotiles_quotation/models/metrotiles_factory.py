# Metrotiles Factory model
#
# This model will create a new field called Factory. This new field will determine what factory does the product
# came from.
from odoo import models, fields


class Factory(models.Model):
    _name = 'metrotiles.factory'
    _description = 'Factory model'

    name = fields.Char(String="Factory")
