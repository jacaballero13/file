# -*- coding: utf-8 -*-

from odoo import models, fields, api


class site_contact(models.Model):
    _inherit = 'sale.order'


    sales_ac        = fields.Many2one('res.users', string="Account Coordinator")
    site_contact    = fields.Char(string="Site Contact Person")
    site_number     = fields.Char(string="Site Contact Number")
    site_permit     = fields.Boolean(string="Requires Permit")
    from_time       = fields.Selection([('1', '12:00 A.M'),
                                        ('2', '01:00 A.M'),
                                        ('3', '02:00 A.M'),
                                        ('4', '03:00 A.M'),
                                        ('5', '04:00 A.M'),
                                        ('6', '05:00 A.M'),
                                        ('7', '06:00 A.M'),
                                        ('8', '07:00 A.M'),
                                        ('9', '08:00 A.M'),
                                        ('10', '09:00 A.M'),
                                        ('11', '10:00 A.M'),
                                        ('12', '11:00 A.M'),
                                        ('13', '12:00 P.M'),
                                        ('14', '01:00 P.M'),
                                        ('15', '02:00 P.M'),
                                        ('16', '03:00 P.M'),
                                        ('17', '04:00 P.M'),
                                        ('18', '05:00 P.M'),
                                        ('19', '06:00 P.M'),
                                        ('20', '07:00 P.M'),
                                        ('21', '08:00 P.M'),
                                        ('22', '09:00 P.M'),
                                        ('23', '10:00 P.M'),
                                        ('24', '11:00 P.M'),],default='9')
    to_time         = fields.Selection([('1', '12:00 A.M'),
                                        ('2', '01:00 A.M'),
                                        ('3', '02:00 A.M'),
                                        ('4', '03:00 A.M'),
                                        ('5', '04:00 A.M'),
                                        ('6', '05:00 A.M'),
                                        ('7', '06:00 A.M'),
                                        ('8', '07:00 A.M'),
                                        ('9', '08:00 A.M'),
                                        ('10', '09:00 A.M'),
                                        ('11', '10:00 A.M'),
                                        ('12', '11:00 A.M'),
                                        ('13', '12:00 P.M'),
                                        ('14', '01:00 P.M'),
                                        ('15', '02:00 P.M'),
                                        ('16', '03:00 P.M'),
                                        ('17', '04:00 P.M'),
                                        ('18', '05:00 P.M'),
                                        ('19', '06:00 P.M'),
                                        ('20', '07:00 P.M'),
                                        ('21', '08:00 P.M'),
                                        ('22', '09:00 P.M'),
                                        ('23', '10:00 P.M'),
                                        ('24', '11:00 P.M'),],default='18')
