# -*- coding: utf-8 -*-
# from odoo import http


# class MetrotilesScrap(http.Controller):
#     @http.route('/metrotiles_scrap/metrotiles_scrap/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/metrotiles_scrap/metrotiles_scrap/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('metrotiles_scrap.listing', {
#             'root': '/metrotiles_scrap/metrotiles_scrap',
#             'objects': http.request.env['metrotiles_scrap.metrotiles_scrap'].search([]),
#         })

#     @http.route('/metrotiles_scrap/metrotiles_scrap/objects/<model("metrotiles_scrap.metrotiles_scrap"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('metrotiles_scrap.object', {
#             'object': obj
#         })
