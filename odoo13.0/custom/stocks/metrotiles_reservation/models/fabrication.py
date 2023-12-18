from odoo import models, fields, api, exceptions


class MetrotilesFabrication(models.Model):
    _name = 'metrotiles.fabrication'

    name = fields.Char()
    source_document = fields.Char("Source")
    deadline = fields.Date('Deadline')
    date_plan_start = fields.Datetime('Date Plan Start')
    date_plan_end = fields.Datetime('Date Plan End')
