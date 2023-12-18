# -*- coding: utf-8 -*-
# from odoo import http


# class MetrotilesCharges(http.Controller):
#     @http.route('/metrotiles_charges/metrotiles_charges/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/metrotiles_charges/metrotiles_charges/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('metrotiles_charges.listing', {
#             'root': '/metrotiles_charges/metrotiles_charges',
#             'objects': http.request.env['metrotiles_charges.metrotiles_charges'].search([]),
#         })

#     @http.route('/metrotiles_charges/metrotiles_charges/objects/<model("metrotiles_charges.metrotiles_charges"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('metrotiles_charges.object', {
#             'object': obj
#         })
