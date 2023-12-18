# *-* coding: utf-8 *-*

from odoo import models, api, fields


class InventoryReportWizard(models.TransientModel):
    _name = 'inventory.report.wizard'
    _description = 'Inventory Report Handler'
    
    warehouse_id = fields.Many2one(comodel_name='stock.warehouse', string="Warehouse", required=True)
    product_id = fields.Many2many(comodel_name='product.product', string="Product", )
    prod_categ = fields.Many2one(comodel_name='product.category', string="Product Category")
    branch_name = fields.Char(related='warehouse_id.name')
    filter_by = fields.Selection(selection=[
                                             ('product', "Product"),
                                             ('product_categ', "Product Category")
                                             ], default='product')
    
    def action_generate_xlsx_report(self):
        data = {
            'warehouse_id': self.warehouse_id.id,
            'product_id': self.product_id.ids,
            'prod_categ': self.prod_categ.id,
            'filter_by': self.filter_by,
        }
        return self.env.ref('metrotiles_inventory_report.inventory_report_xlsx').report_action(self, data=data)

    def action_generate_csv_report(self):
        data = {
            'warehouse_id': self.warehouse_id.id,
            'product_id': self.product_id.ids,
            'prod_categ': self.prod_categ.id,
            'filter_by': self.filter_by,
        }
        return self.env.ref('metrotiles_inventory_report.inventory_report_ccsv').report_action(self, data=data)