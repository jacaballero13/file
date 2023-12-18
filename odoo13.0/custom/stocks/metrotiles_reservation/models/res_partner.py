from odoo import models, fields, api, exceptions


class MetrotilesResPartner(models.Model):
    _inherit = 'res.partner'

    sale_indentions = fields.One2many('metrotiles.sale.indention', 'factory_id', 'Indent Purchase Line', domain=[('balance', '>', 0)])
    total_items_to_purchase = fields.Float('Total Items', compute="get_total_items")
    factory_settings = fields.Many2one('metrotiles.factory.settings')

    def get_total_items(self):
        for rec in self:
           rec.update({
               'total_items_to_purchase': len(rec.sale_indentions)
           })

    def open_create_rfq(self):
        return {
            'name': self.name,
            'res_model': 'res.partner',
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'view_id': self.env.ref('metrotiles_reservation.create_rfq_form').id,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
        }

    def create_rfq(self):
        has_qty_to_purchase = False

        for indent in self.sale_indentions:
            if indent.to_purchase_qty > 0:
                has_qty_to_purchase = True
                break

        if has_qty_to_purchase:
            purchase_order = self.env['purchase.order'].create({'partner_id': self.id, 'picking_type_id': 9})

            for indent in self.sale_indentions:

                if indent.to_purchase_qty > 0:

                    self.env['purchase.order.line'].create({
                        'display_type': False,
                        'sequence': 10,
                        'state': False,
                        'indention_id': indent.id,
                        'product_id': indent.product_id.id,
                        'name': indent.product_id.name,
                        'account_analytic_id': False,
                        'product_qty': indent.to_purchase_qty,
                        'qty_received_manual': 0,
                        'product_uom': indent.product_id.uom_id.id,
                        'date_planned': '2020-07-08 04:36:25',
                        'price_unit': 0,
                        'taxes_id': [[6, False, [2]]],
                        'order_id': purchase_order.id
                    })

                indent.to_purchase_qty = 0

            return {
                'name': purchase_order.name,
                'res_model': 'purchase.order',
                'type': 'ir.actions.act_window',
                'res_id': purchase_order.id,
                'view_mode': 'form',
                'view_type': 'form',
                'target': 'current',
            }

        return