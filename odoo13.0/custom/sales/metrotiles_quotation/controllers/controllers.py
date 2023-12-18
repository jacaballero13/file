# -*- coding: utf-8 -*-
# from odoo import http


# class MetrotilesQuotation(http.Controller):
#     @http.route('/metrotiles_quotation/metrotiles_quotation/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/metrotiles_quotation/metrotiles_quotation/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('metrotiles_quotation.listing', {
#             'root': '/metrotiles_quotation/metrotiles_quotation',
#             'objects': http.request.env['metrotiles_quotation.metrotiles_quotation'].search([]),
#         })

#     @http.route('/metrotiles_quotation/metrotiles_quotation/objects/<model("metrotiles_quotation.metrotiles_quotation"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('metrotiles_quotation.object', {
#             'object': obj
#         })
