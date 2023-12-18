# -*- coding: utf-8 -*-

import datetime
from functools import reduce
from odoo import models, fields
from odoo.exceptions import UserError
import random

class PurchaseTransactionLog(models.AbstractModel):
    _name = 'report.metrotiles_inventory_report.inventory_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    
    def generate_xlsx_report(self, workbook, data, partners):
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

        #Excel Format
        sheet = workbook.add_worksheet('Data')
        bold = workbook.add_format({'bold': True, 'align': 'center', })
        title = workbook.add_format({'bold': True, 'align': 'left'})
        header_row_style = workbook.add_format({'bold': True, 'align': 'center', 'border': True})
        s_no_format = workbook.add_format({'align': 'center'})
        # sheet.merge_range('A1:N1', 'Inventory', title)
        money_format = workbook.add_format({'text_wrap': True, 'num_format': '#,##0.00'})
        
        date_generated = fields.datetime.now().strftime("%B %d, %Y")
        
        row = 3
        col = 0
        s_no = 1
        # Header row
        sheet.write(0, 0, 'INVENTORY REPORT', title)
        sheet.write(1, 0, 'as of: %s' %date_generated, title)
        # sheet.write(1, 7, date_to, header_row_style)
        sheet.set_column(0, 0, 34)
        sheet.set_column(1, 1, 30)
        sheet.set_column(2, 2, 20)
        sheet.set_column(3, 3, 50)
        sheet.set_column(4, 4, 26)
        sheet.set_column(5, 5, 10)
        sheet.set_column(6, 6, 20)
        sheet.set_column(7, 7, 20)
        sheet.set_column(8, 8, 22)
        sheet.set_column(9, 9, 25)
        sheet.set_column(10, 10, 20)
        sheet.set_column(11, 11, 18)
        sheet.set_column(12, 12, 18)
        sheet.set_column(13, 13, 18)
        sheet.set_column(14, 14, 18)
        sheet.set_column(15, 15, 15)
        sheet.write(row, col, 'Internal Reference', header_row_style)
        sheet.write(row, col+1, 'Factory', header_row_style)
        sheet.write(row, col+2, 'Series', header_row_style)
        sheet.write(row, col+3, 'Description', header_row_style)
        sheet.write(row, col+4, 'Variant', header_row_style)
        sheet.write(row, col+5, 'Size', header_row_style)
        sheet.write(row, col+6, 'Public Price', header_row_style)
        sheet.write(row, col+7, 'Sales(Stock View)', header_row_style)
        sheet.write(row, col+8, 'Reserved Qty', header_row_style)
        sheet.write(row, col+9, 'Temp Reserved Qty', header_row_style)
        sheet.write(row, col+10, 'Product Category', header_row_style)
        sheet.write(row, col+11, 'Warehouse', header_row_style)
        sheet.write(row, col+12, 'Piece/Box', header_row_style)
        # sheet.write(row, col+13, 'Qty sold', header_row_style)
        
        row += 1
        for rec in products:
            price = 0 
            price += rec.lst_price
            variant = 'N/A'
            size = 'N/A'
            for attr in rec.product_template_attribute_value_ids:
                if attr.attribute_id.name == 'Variants':
                    variant = attr.name
                elif attr.attribute_id.name == 'Sizes':
                    size = attr.name
            total_sold = random.randint(0, 1000)
            delivery_date = ''
            received_date = ''
            reserved_qty = sum(prod.quantity for prod in self.env['metrotiles.product.reserved'].search([('product_id', '=', rec.id)]))
            temp_reserved_qty = sum(prod.quantity for prod in self.env['metrotiles.product.temp.reserved'].search([('product_id', '=', rec.id)]))
            # sale_product = self.env['sale.order.line'].search([('')])
            # stock_pick_obj = self.env['stock.picking'].search([('origin', '=', rec.name)], limit=1)
            # if stock_pick_obj.scheduled_date:
            #     delivery_date = datetime.datetime.strptime(stock_pick_obj.scheduled_date, '%Y-%m-%d %H:%M:%S')
            #     delivery_date = delivery_date.strftime("%B %d, %Y") if delivery_date else None
            
            # if stock_pick_obj.x_received_date:
            #     received_date = datetime.datetime.strptime(stock_pick_obj.x_received_date, '%Y-%m-%d')
            #     received_date = received_date.strftime("%B %d, %Y")if received_date else None
            sheet.write(row, col, rec.default_code, s_no_format)
            sheet.write(row, col+1, rec.factory_id.name)
            sheet.write(row, col+2, rec.series_id.name)
            sheet.write(row, col+3, rec.name)
            sheet.write(row, col+4, variant)
            sheet.write(row, col+5, size)
            sheet.write(row, col+6, rec.lst_price, money_format)
            sheet.write(row, col+7, rec.sales_reserved_qty)
            sheet.write(row, col+8, reserved_qty)
            sheet.write(row, col+9, temp_reserved_qty)
            sheet.write(row, col+10, rec.categ_id.name)
            sheet.write(row, col+11, rec.branch_id.name)
            sheet.write(row, col+12, rec.pc_box)
            # sheet.write(row, col+13, total_sold)
                

            s_no+=1
            row += 1

        