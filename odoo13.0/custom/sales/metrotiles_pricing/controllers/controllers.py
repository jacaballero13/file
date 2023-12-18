# -*- coding: utf-8 -*-
# from odoo import http


# class MetrotilesDiscount(http.Controller):
#     @http.route('/metrotiles_discount/metrotiles_discount/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/metrotiles_discount/metrotiles_discount/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('metrotiles_discount.listing', {
#             'root': '/metrotiles_discount/metrotiles_discount',
#             'objects': http.request.env['metrotiles_discount.metrotiles_discount'].search([]),
#         })

#     @http.route('/metrotiles_discount/metrotiles_discount/objects/<model("metrotiles_discount.metrotiles_discount"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('metrotiles_discount.object', {
#             'object': obj
#         })
