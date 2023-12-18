

from odoo import api, fields, models
from odoo.fields import first


class StockPicking(models.Model):
    _inherit = "stock.picking"

    returned_ids = fields.Many2many(
        comodel_name="stock.picking",
        compute="_compute_returned_ids",
        string="Returned pickings",
    )
    source_picking_id = fields.Many2one(
        comodel_name="stock.picking",
        compute="_compute_source_picking_id",
        string="Source picking",
    )

    def _compute_returned_ids(self):
        for picking in self:
            picking.returned_ids = picking.mapped(
                "move_lines.returned_move_ids.picking_id"
            )

    @api.depends("move_lines.origin_returned_move_id")
    def _compute_source_picking_id(self):
        """Get source piking from this picking. Only one origin is possible."""
        for picking in self:
            picking.source_picking_id = first(
                picking.mapped("move_lines.origin_returned_move_id.picking_id")
            )

    def action_show_source_picking(self):
        """ Open source picking form action """
        return self.source_picking_id.get_formview_action()
