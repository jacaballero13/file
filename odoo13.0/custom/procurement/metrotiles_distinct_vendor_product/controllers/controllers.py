# -*- coding: utf-8 -*-
# from odoo import http


# class MetrotilesDistinctVendorProduct(http.Controller):
#     @http.route('/metrotiles_distinct_vendor_product/metrotiles_distinct_vendor_product/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/metrotiles_distinct_vendor_product/metrotiles_distinct_vendor_product/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('metrotiles_distinct_vendor_product.listing', {
#             'root': '/metrotiles_distinct_vendor_product/metrotiles_distinct_vendor_product',
#             'objects': http.request.env['metrotiles_distinct_vendor_product.metrotiles_distinct_vendor_product'].search([]),
#         })

#     @http.route('/metrotiles_distinct_vendor_product/metrotiles_distinct_vendor_product/objects/<model("metrotiles_distinct_vendor_product.metrotiles_distinct_vendor_product"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('metrotiles_distinct_vendor_product.object', {
#             'object': obj
#         })
