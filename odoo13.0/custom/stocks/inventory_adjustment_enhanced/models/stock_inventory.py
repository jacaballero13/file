# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

from itertools import product
from operator import inv
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

# from odoo.tools.func import default


class StockInventory(models.Model):
    _inherit = "stock.inventory"

    warehouse_id = fields.Many2one(
        comodel_name="stock.warehouse",
        string="Warehouse",
        states={"draft": [("readonly", False)]},
    )
    cutoff_date = fields.Date(string="Inventory Cut-Off Date")
    filter = fields.Selection(
        string="Inventory of",
        selection="_selection_filter",
        required=True,
        default="none",
        help="If you do an entire inventory, you can choose 'All Products' and it will prefill the inventory with the current stock.  If you only do some products  "
        "(e.g. Cycle Counting) you can choose 'Manual Selection of Products' and the system won't propose anything.  You can also let the "
        "system propose for a single product / lot /... ",
    )
    product_id = fields.Many2one(
        "product.product",
        "Inventoried Product",
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="Specify Product to focus your inventory on a particular Product.",
    )
    category_id = fields.Many2one(
        "product.category",
        "Product Category",
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="Specify Product Category to focus your inventory on a particular Category.",
    )
    hide_on_hand = fields.Boolean(string="Hide On Hand Balance")
    count_tag_ids = fields.One2many(
        "inventory.count.tags", "inventory_id", string="Count Tags"
    )

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('seq.inventory.adjustment')
        return super(StockInventory, self).create(vals)
    
    def get_count_tag(self):
        return self.env["inventory.count.tags"].search([("inventory_id", "=", self.id)])

    @api.model
    def _selection_filter(self):
        """Get the list of filter allowed according to the options checked
        in 'Settings\Warehouse'."""
        res_filter = [
            ("none", _("All products")),
            ("category", _("One product category")),
            ("product", _("One product only")),
            ("partial", _("Select products manually")),
        ]
        return res_filter

    @api.onchange("filter")
    def _onchange_filter(self):
        self.ensure_one()
        if self.filter not in ("product", "product_owner"):
            self.product_id = False
        if self.filter != "category":
            self.category_id = False
        if self.filter == "product":
            self.exhausted = True
            if self.product_id:
                return {
                    "domain": {
                        "product_id": [
                            ("product_tmpl_id", "=", self.product_id.product_tmpl_id.id)
                        ]
                    }
                }

    # @api.onchange('location_id')
    # def _onchange_location_id(self):
    #     if self.location_id.company_id:
    #         self.company_id = self.location_id.company_id

    @api.constrains("filter", "product_id", "lot_id")
    def _check_filter_product(self):
        if (
            self.filter == "none"
            and self.product_id
            and self.location_id
            and self.lot_id
        ):
            return
        if self.filter not in ("product", "product_owner") and self.product_id:
            raise ValidationError(
                _("The selected product doesn't belong to that owner..")
            )

    def action_start(self):
        for inventory in self.filtered(lambda x: x.state not in ("done", "cancel")):
            vals = {"state": "confirm", "date": fields.Datetime.now()}
            if (inventory.filter != "partial") and not inventory.line_ids:
                vals.update(
                    {
                        "line_ids": [
                            (0, 0, line_values)
                            for line_values in inventory._get_inventory_lines_values()
                        ]
                    }
                )
            inventory.write(vals)
        return True

    def action_open_inventory_lines(self):
        res = super(StockInventory,self).action_open_inventory_lines()
        ctx = res['context']
        ctx['hide_on_hand'] = self.hide_on_hand
        res['context'] = ctx
        return res

    def action_open_inventory_tags(self):
        return {
            "name": _("Inventory Count Tags"),
            "view_mode": "tree,form",
            "res_model": "inventory.count.tags",
            "view_id": False,
            "type": "ir.actions.act_window",
            "domain": [("inventory_id", "in", self.ids)],
            "context": {
                "default_inventory_id": self.id,
            },
        }
    
    def print_count_tag_list(self):
        if not self.count_tag_ids:
            raise UserError(_("No Count Tags Found"))
        return self.env.ref('inventory_adjustment_enhanced.inventory_adjustment_count_tag_list_report').report_action(self)


    def action_cancel_draft(self):
        super(StockInventory,self).action_cancel_draft()
        self.count_tag_ids.unlink()
        self.write({'state': 'cancel'})
    
    def action_set_draft(self):
        self.line_ids.unlink()
        self.count_tag_ids.unlink()
        self.write({'state': 'draft'})


    def action_validate(self):
        self.ensure_one()
        for each in self.line_ids:
            if each.count_tag_id:
                each.count_tag_id.state = "confirm"
        return super(StockInventory,self).action_validate()


class StockInventoryLine(models.Model):
    _inherit = "stock.inventory.line"

    # loc_id = fields.Many2one(comodel_name="stock.location", related="inventory_id.location_id")
    unit_cost = fields.Float(compute="_compute_amount")
    on_hand_amt = fields.Float(compute="_compute_amount")
    counted_amt = fields.Float(compute="_compute_amount")
    diff_amt = fields.Float(compute="_compute_amount")
    count_tag_id = fields.Many2one(comodel_name="inventory.count.tags")

    @api.depends("product_qty", "theoretical_qty")
    def _compute_amount(self):
        for line in self:
            line.unit_cost = line.product_id.standard_price
            line.on_hand_amt = line.theoretical_qty * line.product_id.standard_price
            line.counted_amt = line.product_qty * line.product_id.standard_price
            line.diff_amt = line.difference_qty * line.product_id.standard_price

    @api.model
    def create(self, vals):
        res = super(StockInventoryLine, self).create(vals)
        # res.cr.commit()
        if not vals.get('count_tag_id'):
            res.count_tag_id = self.env["inventory.count.tags"].create(
                {
                    "product_id": vals.get("product_id"),
                    "inventory_id": vals.get("inventory_id"),
                    "theoretical_qty": vals.get("theoretical_qty"),
                    "difference_qty": vals.get("difference_qty"),
                    "product_uom_id": vals.get("product_uom_id"),
                    "product_qty": vals.get("product_qty"),
                    "location_id": vals.get("location_id"),
                    "prod_lot_id": vals.get("prod_lot_id"),
                    "encoded_by": res.create_uid.id,
                    "date_encoded": res.create_date,
                    "state":"draft",
                    # "inventory_line_id": res.id,
                }
            )
        return res

    def write(self, vals):
        res = super(StockInventoryLine, self).write(vals)
        for each in self:
            each.count_tag_id.product_qty = each.product_qty
        return res
    

    def view_tags(self):
        tag_ids = [each.count_tag_id.id for each in self]
        return {
            "name": _("Inventory Count Tags"),
            "view_mode": "tree,form",
            "res_model": "inventory.count.tags",
            "view_id": False,
            "type": "ir.actions.act_window",
            "domain": [("id", "in", tag_ids)],
        }



class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        adjustment = self.env["stock.inventory"].search([("state", "=", "confirm")])
        if adjustment:
            raise ValidationError(
                _("Transfer is not allowed until 'Inventory Adjustment' is in Progress")
            )
        return super(StockPicking, self).button_validate()

        # product_ids = []
        # picking_prods = []
        # for line in self.move_ids_without_package:
        #     picking_prods.append(line.product_id.id)
        # for invtr in inventory:
        #     product_ids += invtr.product_ids.ids
        # if set(picking_prods) & set(product_ids):
        #     raise ValidationError(
        #         _("Transfer is not allowed until 'Inventory Adjustment' is in Progress")
        #     )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4
