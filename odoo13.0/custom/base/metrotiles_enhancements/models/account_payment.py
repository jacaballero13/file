from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountPayment(models.Model):
    _inherit = 'account.payment'


    memo_date = fields.Char(string="Memo/Request Date")
    contract_ref = fields.Char(string="Source Document", compute='get_source_doc', store=True)
    contract_date = fields.Datetime(string="Order Date", compute='get_source_doc', store=True)
    sales_person = fields.Many2one('res.users', string="Salesperson", compute='get_source_doc', store=True)

    show_button_draft = fields.Boolean(
        compute='_compute_show_button_draft',
        string="Show Reset to Draft Button",
        store=False,
        compute_sudo=True
    )

    @api.depends('state')
    def _compute_show_button_draft(self):
        group_show_button_draft = self.env.ref('metrotiles_enhancements.group_show_button_draft')
        for move in self:
            if self.state == 'posted':
                move.show_button_draft = group_show_button_draft in self.env.user.groups_id
            else:
                move.show_button_draft = True

    @api.depends('invoice_lines.invoice_id', 'invoice_lines.select', 'invoice_lines')
    def get_source_doc(self):
        for rec in self:
            for inv in rec.invoice_lines:
                for invoice in inv.invoice_id:
                    sale_order = self.env['sale.order'].search([('name','=', invoice.invoice_origin)])
                    if sale_order and inv.select:
                        rec.contract_ref = sale_order.name
                        rec.contract_date = sale_order.date_order or ""
                        rec.sales_person = sale_order.user_id.id or ""


