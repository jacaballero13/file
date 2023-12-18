# -*- coding: utf-8 -*-

from odoo import fields, models,api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    rfq_sequence_id = fields.Many2one('ir.sequence', 
        string='RFQ Sequence')
    po_sequence_id = fields.Many2one('ir.sequence', 
        string='PO Sequence')
    
    
    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            rfq_sequence_id = int(self.env['ir.config_parameter'].sudo().get_param('metrotiles_rfq_sequence.rfq_sequence_id')),
            po_sequence_id = int(self.env['ir.config_parameter'].sudo().get_param('metrotiles_rfq_sequence.po_sequence_id')),
        )
        return res
    
    
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('metrotiles_rfq_sequence.rfq_sequence_id', self.rfq_sequence_id.id)
        self.env['ir.config_parameter'].sudo().set_param('metrotiles_rfq_sequence.po_sequence_id', self.po_sequence_id.id)

