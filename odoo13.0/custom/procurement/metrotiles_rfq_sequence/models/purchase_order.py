# -*- coding: utf-8 -*-
from odoo import fields, models,api,_
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    @api.model
    def create(self, vals):
        sequence = self.env['ir.config_parameter'].sudo().get_param('metrotiles_rfq_sequence.rfq_sequence_id')
        sequence_id = self.env['ir.sequence'].search([('id','=',sequence)])
        if not sequence_id:
            raise UserError(_('Please select sequence for RFQ in Purchase->Configuration->Settings.'))
        name = sequence_id.next_by_id()
        vals['name'] = name
        return super(PurchaseOrder, self).create(vals)
    
    
    def button_confirm(self, force=False):
        sequence = self.env['ir.config_parameter'].sudo().get_param('metrotiles_rfq_sequence.po_sequence_id')
        sequence_id = self.env['ir.sequence'].search([('id','=',sequence)])
        if not sequence_id:
            raise UserError(_('Please select sequence for PO in Purchase->Configuration->Settings.'))
        name = sequence_id.next_by_id()
        self.write({'name': name})
        return super(PurchaseOrder, self).button_confirm()


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    
    shipment_reference_id = fields.Many2one(comodel_name='shipment.number', compute='_get_lineup_shipment_reference')
		
    @api.depends('product_id')
    def _get_lineup_shipment_reference(self):
        for rec in self:
            shipment_ref = self.env['metrotiles_procurement.proforma_invoice_item'].search([('order_line', '=', rec.id)])
            if shipment_ref:
                rec.shipment_reference_id = shipment_ref.shipment_id.id
                
            else:
                rec.shipment_reference_id = None