from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountInvoice(models.Model):
    _inherit = 'account.move'

    amount_vat = fields.Float(compute='get_all_taxes')
    manual_si = fields.Char(string="Manual SI")
    manual_date = fields.Datetime(string="Manual SI Date")
    order_date = fields.Datetime(string="Order Date", compute="get_order_date")
    sales_person = fields.Many2one('res.users', string="Salesperson", compute='get_order_date', store=True)

    
    show_button_draft = fields.Boolean(
        compute='_compute_show_button_draft',
        string="Show Reset to Draft Button",
        store=False,
        compute_sudo=True
    )

    def _compute_show_button_draft(self):
        group_show_button_draft = self.env.ref('metrotiles_enhancements.group_show_button_draft')
        user_groups = self.env.user.groups_id
        for move in self:
            if self.state == 'posted':
                move.show_button_draft = group_show_button_draft in self.env.user.groups_id
            else:
                move.show_button_draft = True
    @api.depends('invoice_origin')
    def get_order_date(self):
        for rec in self:
            sale_order = self.env['sale.order'].search([('name','=', rec.invoice_origin)])
            if sale_order:
                rec.order_date = sale_order.date_order
                rec.sales_person = sale_order.user_id.id or ""
            else:
                rec.order_date = ""
    @api.onchange('invoice_line_ids')
    def get_all_taxes(self):
        taxes = 0
        for rec in self.invoice_line_ids:
            taxes +=  ((rec.price_subtotal*rec.tax_ids.amount)/100)
            
        self.amount_vat = taxes
