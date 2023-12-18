# -*- coding: utf-8 -*-
# from odoo import http


# class MetrotilesDescriptionModification(http.Controller):
#     @http.route('/metrotiles_description_modification/metrotiles_description_modification/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/metrotiles_description_modification/metrotiles_description_modification/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('metrotiles_description_modification.listing', {
#             'root': '/metrotiles_description_modification/metrotiles_description_modification',
#             'objects': http.request.env['metrotiles_description_modification.metrotiles_description_modification'].search([]),
#         })

#     @http.route('/metrotiles_description_modification/metrotiles_description_modification/objects/<model("metrotiles_description_modification.metrotiles_description_modification"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('metrotiles_description_modification.object', {
#             'object': obj
#         })
