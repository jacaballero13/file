from odoo import models,api, fields,_
import datetime


class SaleOrderRefractor(models.Model):
    _inherit = 'sale.order'
    
    def action_confirm(self):
        # if self._get_forbidden_state_confirm() & set(self.mapped('state')):
        #     raise exceptions.UserError(_(
        #         'It is not allowed to confirm an order in the following states: %s'
        #     ) % (', '.join(self._get_forbidden_state_confirm())))

        for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
            order.message_subscribe([order.partner_id.id])

        if self.state is not 'sale':
            for line in self.order_line:
                location_id = line.pallet_id.location_id.id
                if not line.to_fabricate:
                    for prod_temp_reserve in line.product_temp_reserved:
                        # stock_loc_id = self.env['stock.quant'].search([('location_id','=', location_id), ('product_id', '=', line.product_id.id)])
                        self.env['metrotiles.product.reserved'].sudo().create({
                            'stock_location_id': location_id,
                            'package_id': line.package_id.id,
                            'quantity': prod_temp_reserve.quantity,
                            'sale_line_id': line.id,
                            'product_id': line.product_id.id,
                        })
                        prod_temp_reserve.unlink()
                else:
                    line.remove_temp_reserved(line.warehouse_id.lot_stock_id, line.bom.bom_line_ids[0].product_id, line.temp_reserved, line.package_id.id)
                    self.env['mrp.production'].sudo().create_from_so_line(so_line=line)

                if line.indent > 0:
                    self.env['metrotiles.sale.indention'].sudo().create({
                        'quantity': line.indent,
                        'sale_line_id': line.id,
                        'factory_id': line.factory_id.id,
                        'to_fabricate': False
                    })
                # Create Indent from fabrication
                fab_quant = line.product_uom_qty if line.bom.id else 0
                # if line.bom.bom_line_ids.product_id.sales_reserved_qty < fab_quant:
                #     if line.bom.id and line.to_fabricate:
                #         self.env['metrotiles.sale.indention'].sudo().create({
                #             'quantity': fab_quant - line.bom.bom_line_ids.product_id.sales_reserved_qty,
                #             'sale_line_id': line.id,
                #             'factory_id': line.factory_id.id,
                #             'to_fabricate': True
                #         })
                        
                if line.to_fabricate:
                    fabricated_raw_matt_indent = self.env['metrotiles.product.temp.reserved'].sudo().search([('sale_line_id','=', line.id)])
                    fabricated_raw_matt_indent.unlink()
                    if fabricated_raw_matt_indent:
                        self.env['metrotiles.product.reserved'].sudo().create({
                                    'quantity': line.bom.bom_line_ids.product_qty,
                                    'sale_line_id': line.id,
                                    'product_id': line.bom.bom_line_ids.product_id.id
                                })
                
        self.write({
            'state': 'sale',
            'date_order': fields.Datetime.now()
        })

        self._action_confirm()

        if self.env.user.has_group('sale.group_auto_done_setting'):
            self.action_done()

        return True
