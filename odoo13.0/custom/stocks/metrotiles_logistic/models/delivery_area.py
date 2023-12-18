from odoo import api, fields, models, _


class DeliveryArea(models.Model):
    _name = 'delivery.area'
    _rec_name = 'name'
    _description = 'Delivery Area'
    
    name = fields.Char('Delivery Area')