# -*- coding: utf-8 -*-
# from odoo import http


# class MetrotilesSales(http.Controller):
#     @http.route('/metrotiles_sales/metrotiles_sales/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/metrotiles_sales/metrotiles_sales/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('metrotiles_sales.listing', {
#             'root': '/metrotiles_sales/metrotiles_sales',
#             'objects': http.request.env['metrotiles_sales.metrotiles_sales'].search([]),
#         })

#     @http.route('/metrotiles_sales/metrotiles_sales/objects/<model("metrotiles_sales.metrotiles_sales"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('metrotiles_sales.object', {
#             'object': obj
#         })
