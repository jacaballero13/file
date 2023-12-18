# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    
    def action_adjustment_wizard(self):
        order_id = self.env['sale.order'].browse(self._context.get('active_ids', False))
        view_id = self.env.ref('metrotiles_sales_adjustment.metrotiles_saf_wizard_view_form')
        if view_id:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Create Sales Adjustment'),
                'res_model': 'metrotiles.saf.wizard',
                'target': 'new',
                'view_id':view_id.id,
                'view_mode': 'form',
                'context': {'default_sales_order_id': order_id.id}
            }
    # We must unlink temp. reserved qty if contract is not yet approved
    # Allow manager access to cancel or set quotation in draft.
    def action_cancel(self):
        for rec in self:
            if not self.user_has_groups('sales_team.group_sale_manager'):
                raise UserError(_("Sorry! You're not allowed to Cancel Quotation. Pls. contact your Admin/Manager."))
            temp_reserved = self.env['metrotiles.product.temp.reserved'].search([('order_name','=',rec.name)])
            reserved_prod = self.env['metrotiles.product.reserved'].search([('order_name','=',rec.name)])
            for reserved in reserved_prod:
                if reserved_prod:
                    reserved.unlink()
            for temp in temp_reserved:
                if temp_reserved and rec.state in ['draft', 'to_approve', 'sent']:
                    temp.unlink()
            indent_ids = self.env['metrotiles.sale.indention'].search([('name', '=', rec.name )])
            for indent in indent_ids:
                if indent:
                    indent.unlink()
        return super(SaleOrder, self).action_cancel()

    def action_draft(self):
        # view_id = self.env.ref('metrotiles_sales_adjustment.metrotiles_saf_wizard_view_form')
        if not self.user_has_groups('sales_team.group_sale_manager'):
            raise UserError(_("Sorry! You're not allowed to Set Quotation in Draft. Pls. contact your Admin/Manager."))
        # if view_id:
        #     return {
        #         'type': 'ir.actions.act_window',
        #         'name': _('Create Sales Adjustment'),
        #         'res_model': 'metrotiles.saf.wizard',
        #         'target': 'new',
        #         'view_id':view_id.id,
        #         'view_mode': 'form',
        #         'context': {'default_sales_order_id': order_id.id}
        #     }
        return super(SaleOrder, self).action_draft()