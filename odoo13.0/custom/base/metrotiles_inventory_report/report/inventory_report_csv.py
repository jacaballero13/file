from odoo import models, fields, api, tools
from odoo.exceptions import ValidationError,UserError
import logging
_logger = logging.getLogger(__name__)

class InventoryReportCSV(models.AbstractModel):
    _name = 'report.metrotiles_inventory_report.inventory_report_ccsv'
    _inherit = 'report.report_csv.abstract'

    def generate_csv_report(self, writer, data, partners):
        domain = [('active', '=', True)]
        filters = data.get('filter_by')
        # Warehouse Data
        warehouse_id = data.get('warehouse_id')
        warehouse_name = self.env['stock.warehouse'].search([('id', '=', warehouse_id)])
        domain.append(('branch_id.name', '=', warehouse_name.name))

        #Product Data
        if filters == 'product':
            prod_ids = data.get('product_id')
            if len(prod_ids) > 0:
                domain.append(('id', 'in', prod_ids))
                
        if filters == 'product_categ':
            prod_category = data.get('prod_categ')
            prod_categ_id = self.env['product.category'].browse(prod_category)
            domain.append(('categ_id', '=', prod_categ_id.id))
        
        products = self.env['product.product'].search(domain)

        writer.writeheader()
      
        for rec in products:
            # price = 0 
            # price += rec.lst_price
            variant = 'N/A'
            size = 'N/A'
            for attr in rec.product_template_attribute_value_ids:
                if attr.attribute_id.name == 'Variants':
                    variant = attr.name
                elif attr.attribute_id.name == 'Sizes':
                    size = attr.name
            delivery_date = ''
            received_date = ''
            reserved_qty = sum(prod.quantity for prod in self.env['metrotiles.product.reserved'].search([('product_id', '=', rec.id)]))
            temp_reserved_qty = sum(prod.quantity for prod in self.env['metrotiles.product.temp.reserved'].search([('product_id', '=', rec.id)]))
            
            writer.writerow({
                    'Internal Reference': rec.default_code,
                    'Factory':rec.factory_id.name,
                    'Series':rec.series_id.name,
                    'Description':rec.name,
                    'Variant': variant,
                    'Size': size,
                    # 'Public Price': price,
                    'Sales(Stock View)': rec.sales_reserved_qty,
                    'Reserved Qty': reserved_qty,
                    'Temp Reserved Qty': temp_reserved_qty,
                    'Product Category': rec.categ_id.name,
                    'Warehouse': rec.branch_id.name,
                    'Box': rec.pc_box,
                })
       

    def csv_report_options(self):
        res = super().csv_report_options()
        res['fieldnames'].append('Internal Reference')
        res['fieldnames'].append('Factory')
        res['fieldnames'].append('Series')
        res['fieldnames'].append('Description')
        res['fieldnames'].append('Variant')
        res['fieldnames'].append('Size')
        # res['fieldnames'].append('Public Price')
        res['fieldnames'].append('Sales(Stock View)')
        res['fieldnames'].append('Reserved Qty')
        res['fieldnames'].append('Temp Reserved Qty')
        res['fieldnames'].append('Product Category')
        res['fieldnames'].append('Warehouse')
        res['fieldnames'].append('Box')
        res['delimiter'] = ','
        return res