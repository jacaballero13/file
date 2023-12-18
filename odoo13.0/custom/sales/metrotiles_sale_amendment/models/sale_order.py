from odoo import models, fields, api, exceptions


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sale_order_version_id = fields.Many2one('metrotiles.sale.order.version', string="Sale Order Versions")
    to_cancel_contract = fields.Boolean(string="Cancel Contract", default=False)

    previous_version = fields.Many2one('metrotiles.sale.order.version', store=False, compute="get_sale_order_previous_version")
    version_number = fields.Integer(store=False, compute="get_sale_order_get_previous_version_values")
    previous_version_discount_value = fields.Float(store=False, compute="get_sale_order_get_previous_version_values")
    previous_version_discount_type = fields.Char(store=False, compute="get_sale_order_get_previous_version_values")
    previous_vatable = fields.Boolean(store=False, compute="get_sale_order_get_previous_version_values")
    discount_value_changed = fields.Boolean(store=False, compute="get_sale_order_get_previous_version_values")
    discount_type_changed = fields.Boolean(store=False, compute="get_sale_order_get_previous_version_values")
    previous_version_amount_tax = fields.Monetary(store=False, compute="get_sale_order_get_previous_version_values")
    amount_tax_changed = fields.Boolean(store=False, compute="get_sale_order_get_previous_version_values")
    vatable_changed = fields.Boolean(store=False, compute="get_sale_order_get_previous_version_values")

    is_creating_architect = fields.Boolean(
        store=False,
        default=lambda self: self.env.context.get('cancel_contract', False)
    )

    state = fields.Selection(selection_add=[
        ('sale_adjustment', 'Sale Adjustment'),
        ('pending_sale_adjustment', 'Pending Sale Adjustment'),
        ('approve_prcmnt', 'Waiting to Approve by Procurement'),
        ('approve_acctng', 'Waiting to Approve by Accounting'),
        ('approve_admin', 'Waiting to Approve by Admin'),
        ('sale_adjustment_approved', 'Sale Adjustment Approved'),
        ('outdated_version', 'Outdated Version')
    ])


    @api.depends('sale_order_version_id')
    def get_sale_order_previous_version(self):
        for rec in self:
            rec.update({'previous_version': rec.sale_order_version_id.get_previous_version()})

    @api.depends('previous_version')
    def get_sale_order_get_previous_version_values(self):
        for rec in self:
            prev_discount = rec.previous_version.discount_value
            prev_discount_type = rec.previous_version.discount_type
            prev_amount_tax = rec.previous_version.amount_tax
            prev_vatable = rec.previous_version.vatable
            rec.update({
                'version_number': rec.sale_order_version_id.version,
                'previous_version_discount_value': prev_discount,
                'previous_version_discount_type': str(prev_discount_type).title(),
                'previous_version_amount_tax': prev_amount_tax,
                'previous_vatable': prev_vatable,
                'discount_value_changed': rec.discount_value != prev_discount,
                'discount_type_changed': prev_discount_type != rec.discount_type,
                'amount_tax_changed': rec.amount_tax != prev_amount_tax,
                'vatable_changed': rec.vatable != prev_vatable
            })


    @api.model_create_multi
    def create(self, vals_list):
        created_ = super(SaleOrder, self).create(vals_list)
        if not created_.sale_order_version_id.version:
            created_.write({'sale_order_version_id': self.env['metrotiles.sale.order.version'].create(
                {'sale_order_id': created_.id, 'root_sale_order_id': created_.id, 'version': 1})})

        return created_

    def cancel_stock_picking(self):
        for pick in self.env['stock.picking'].search([('sale_id', '=', self.id)]):
            pick.action_cancel()

    def create_new_version(self):
        self.ensure_one()
        # self.write({'state': 'outdated_version'})

        order_lines = self.order_line
        architects = self.architect_ids
        designers = self.designer_ids
        order_name = self.name
        copy = self.copy(
            default={
                'state': 'sale_adjustment',
                'name': "{}/v{}".format(order_name, self.sale_order_version_id.version + 1),
                'origin': order_name,
                'order_line': [],
                'architect_ids': [],
                'designer_ids': []
            })

        for line in order_lines:
            cop = line.copy(default={
                'order_id': copy.id,
            })

            cop.write({'previous_version_id': cop.previous_version_id.create({'sale_order_line_id': line.id})})

        for line in architects:
            cop = line.copy(default={
                'architect_sale_id': copy.id,
            })

            cop.write({'previous_version_id': cop.previous_version_id.create({'architect_id': line.id})})

        for line in designers:
            cop = line.copy(default={
                'designer_sale_id': copy.id,
            })

            cop.write({'previous_version_id': cop.previous_version_id.create({'designer_prev_id': line.id})})

        copy.write({'sale_order_version_id': self.env['metrotiles.sale.order.version'].create({
                    'sale_order_id': copy.id,
                    'root_sale_order_id': copy.sale_order_version_id.root_sale_order_id.id,
                    'version': self.sale_order_version_id.version + 1
                })})

        return {
            'type': 'ir.actions.act_window',
            'name': ('Sales Order'),
            'res_model': 'sale.order',
            'res_id': copy.id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'current',
            'nodestroy': True,
        }

    def roll_back_sale_adjustment(self):
        previous_version = self.sale_order_version_id.get_previous_version()
        previous_version.write({'state': 'sale'})

        self.action_cancel()
        self.unlink()

        return {
            'type': 'ir.actions.act_window',
            'name': ('Sales Order'),
            'res_model': 'sale.order',
            'res_id': previous_version.sale_order_id.id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'current',
            'nodestroy': True,
        }

    def sale_adjustment_apply_for_approval(self):
        self.update({'state': 'approve_prcmnt'})

    def sale_adjustment_approve_prcmnt(self):
        self.update({'state': 'approve_acctng'})

    def sale_adjustment_approve_acctng(self):
        self.update({'state': 'approve_admin'})

    def cancel_contract(self):
        self.update({'state': 'pending_sale_adjustment', 'to_cancel_contract': True})

    def approve_sale_adjustment(self):
        for rec in self:
            if self.to_cancel_contract:
                self.update({'state': 'cancel'})
                self.action_cancel()
                # self.cancel_stock_picking()
            else:
                for each in rec.order_line:
                    if each.indent > 0:
                        indention_id = self.env['metrotiles.sale.indention'].search([('contract_ref', '=', self.origin), ('product_id', '=', each.product_id.id)])
                        if indention_id:
                            indention_id.update({'quantity': each.product_uom_qty, 'balance': each.product_uom_qty})
                self.update({'state': 'sale_adjustment_approved'})

        # previous_version = self.sale_order_version_id.get_previous_version()

        # previous_version.sale_order_id.cancel_stock_picking()

    def action_sale_adjustment_refuse(self, reason):
        self.filtered(lambda r: r.state == 'pending_sale_adjustment').write({
            'state': 'sale_adjustment',
            'to_cancel_contract': False
        })

        for rec in self:
            rec.message_post_with_view('metrotiles_sale_amendment.metrotiles_sale_order_template_declined_reason',
                                       values={'reason': reason, 'name': rec.name, 'state': rec.state})
        return True

    def action_sale_adjustment_cancel_contract_request(self, reason):
        self.filtered(lambda r: r.state == 'sale_adjustment').write({
            'state': 'pending_sale_adjustment',
            'to_cancel_contract': True
        })

        for rec in self:
            rec.message_post_with_view('metrotiles_sale_amendment.metrotiles_sale_order_template_cancel_contract_reason',
                                       values={'reason': reason, 'name': rec.name, 'state': rec.state})

        return True