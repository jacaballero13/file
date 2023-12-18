# -*- coding: utf-8 -*-
from odoo import api, fields, models, SUPERUSER_ID, _
from datetime import datetime

class ProformaInvoiceItems(models.Model):
    _inherit = 'metrotiles_procurement.proforma_invoice_item'

    bill_id = fields.Many2one(comodel_name='shipment.bill_lading', string="BOL")

class BillOfLading(models.Model):
    _inherit = 'shipment.bill_lading'

    shipment_id = fields.Many2one(comodel_name='shipment.number', string="Shipment No.", readonly=False)
    container_no = fields.Many2one(comodel_name="container.number", string="Container No.", related="shipment_id.container_no", readonly=False)

    bill_line = fields.One2many(comodel_name='metrotiles_procurement.proforma_invoice_item', inverse_name='bill_id', 
                        related='shipment_id.proforma_invoice_item', 
                        string="Bill Lading", 
                        store=True)

    @api.onchange('shipment_id')
    def _onchange_container(self):
        for rec in self:
            if rec.shipment_id:
                for container in rec.shipment_id.assign_container_line:
                    rec.update({
                        'xx_ets': container.xx_ets,
                        'xx_eta': container.xx_eta,
                    })