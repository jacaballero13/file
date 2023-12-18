from odoo import models, fields, api, exceptions


class ArchitectPrevVersion(models.Model):
    _name = 'metrotiles.architect.prev.version'
    _inherits = {'metrotiles.architect': 'architect_id'}

    def name_get(self):
        record = []

        for field in self:
            record.append((field.id, field.architect_id.id))

        return record


class Architect(models.Model):
    _inherit = 'metrotiles.architect'

    previous_version_id = fields.Many2one('metrotiles.architect.prev.version', string="Previous Version")
    version_status = fields.Char(store=False, string="Version Status")


class CommissionChanges(models.Model):
    _inherit = "sale.order"

    architect_changes = fields.One2many('metrotiles.architect', store=False, compute="get_architect_changes")

    def get_architect_changes(self):
        for rec in self:
            prev = rec.sale_order_version_id.get_previous_version()
            order_lines = rec.env['metrotiles.architect'].search(
                ['|', ('architect_sale_id', '=', prev.sale_order_id.id),
                 '&', ('previous_version_id', '=', None),
                 ('architect_sale_id', '=', rec.id)],
                order="id asc")

            rec.update({'architect_changes': order_lines})

            return order_lines


class DesignerPrevVersion(models.Model):
    _name = 'metrotiles.designer.prev.version'
    _inherits = {'metrotiles.designer': 'designer_prev_id'}

    def name_get(self):
        record = []

        for field in self:
            record.append((field.id, field.designer_prev_id.id))

        return record


class Designer(models.Model):
    _inherit = 'metrotiles.designer'

    previous_version_id = fields.Many2one('metrotiles.designer.prev.version', string="Previous Version")
    version_status = fields.Char(store=False, string="Version Status")


class DesignerCommissionChanges(models.Model):
    _inherit = "sale.order"

    designer_changes = fields.One2many('metrotiles.designer', store=False, compute="get_designer_changes")

    def get_designer_changes(self):
        for rec in self:
            prev = rec.sale_order_version_id.get_previous_version()

            designers = rec.env['metrotiles.designer'].search(
                ['|', ('designer_sale_id', '=', prev.sale_order_id.id),
                 '&', ('previous_version_id', '=', None),
                 ('designer_sale_id', '=', rec.id)],
                order="id asc")

            rec.update({'designer_changes': designers})

            print(designers)

            return designers
