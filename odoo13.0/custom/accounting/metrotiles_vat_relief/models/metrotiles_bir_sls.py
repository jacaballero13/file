# -*- coding: utf-8 -*-

from odoo import models, fields, api

class MetrotilesBirSls(models.Model):
    ######################
    # Private attributes #
    ######################
    _name = 'metrotiles.bir_sls'
    _rec_name = 'mt_move_id'
    
    
    mt_move_id = fields.Many2one('account.move', string="AR Vouchers")
    mt_branch = fields.Many2one('res.branch', "Branch")
    
    mt_date = fields.Date("POSTING DATE")
    mt_ref = fields.Char("SI NO.")
    mt_tin = fields.Char("TIN NO.")
    mt_partner_id = fields.Many2one('res.partner', string="CLIENTS NAME")
    mt_address = fields.Char("ADDRESS") 
    
    mt_services = fields.Float("SERVICES", default=0.00)
    mt_goods = fields.Float("GOODS", default=0.00)
    mt_rental = fields.Float("RENTAL", default=0.00)
    
    mt_zero_rated = fields.Float("ZERO RATED", default=0.00)
    mt_output_tax = fields.Float("AMOUNT OF OUTPUT TAX", default=0.00)
    mt_gross_sales = fields.Float("AMOUNT OF GROSS SALES", default=0.00)
    mt_account_id = fields.Many2one('account.account', "ACCOUNT")