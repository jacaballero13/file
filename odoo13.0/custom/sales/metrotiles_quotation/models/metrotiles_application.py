# Metrotiles Application model
#
# This model will create a new field called Application. This new field will determine where the product will be
# applied in the particular location by the installation.
from odoo import models, fields


class Application(models.Model):
    _name = 'metrotiles.application'
    _description = 'Application model'

    name = fields.Char(string="Application", required=True)
