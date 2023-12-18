# -*- coding: utf-8 -*-
# from odoo import http


# class MetrotilesArchitectPage(http.Controller):
#     @http.route('/metrotiles_architect_page/metrotiles_architect_page/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/metrotiles_architect_page/metrotiles_architect_page/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('metrotiles_architect_page.listing', {
#             'root': '/metrotiles_architect_page/metrotiles_architect_page',
#             'objects': http.request.env['metrotiles_architect_page.metrotiles_architect_page'].search([]),
#         })

#     @http.route('/metrotiles_architect_page/metrotiles_architect_page/objects/<model("metrotiles_architect_page.metrotiles_architect_page"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('metrotiles_architect_page.object', {
#             'object': obj
#         })
