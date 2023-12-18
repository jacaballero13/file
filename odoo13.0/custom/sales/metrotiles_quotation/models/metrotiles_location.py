# Metrotiles Location model
#
# This model will create a new field called Location. This new field will determine where the product will be
# installed by the installation.
from odoo import models, fields


class Location(models.Model):
    _name = 'metrotiles.location'
    _description = 'Location model'

    name = fields.Char(string="Location", required=True)
