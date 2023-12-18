# -*- coding: utf-8 -*-

from email.policy import default
from unittest.mock import DEFAULT
from odoo import models, fields, api

class MetrotilesBirSlp(models.Model):
    ######################
    # Private attributes #
    ######################
    _name = 'metrotiles.bir_slp'
    _description = "Summary List of Purchase"
    _rec_name = 'mt_move_id'
    
    mt_move_id = fields.Many2one('account.move', string="AP Vouchers")
    mt_branch = fields.Many2one('res.branch', "Branch")
    
    mt_date = fields.Date("POSTING DATE")
    mt_ref = fields.Char("REF NO.")
    mt_tin = fields.Char("TIN NO.")
    mt_partner_id = fields.Many2one('res.partner', string="SUPPLIERS NAME")
    mt_address = fields.Char("ADDRESS") 
    
    mt_net_vat = fields.Float("NET OF VAT", default=0.00)
    mt_services = fields.Float("SERVICES", default=0.00)
    mt_goods = fields.Float("GOODS", default=0.00)
    mt_capital = fields.Float("CAPITAL", default=0.00)
    
    mt_input = fields.Float("INPUT VAT", default=0.00)
    mt_gross_amount = fields.Float("GROSS AMOUNT")
    mt_nvat = fields.Float("NON VAT")
    mt_account_id = fields.Many2one('account.account', "EXPENSE ACCOUNT")