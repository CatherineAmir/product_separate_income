# -*- coding: utf-8 -*-
# from odoo import http


# class CruizeAccount(http.Controller):
#     @http.route('/cruize_account/cruize_account', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cruize_account/cruize_account/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('cruize_account.listing', {
#             'root': '/cruize_account/cruize_account',
#             'objects': http.request.env['cruize_account.cruize_account'].search([]),
#         })

#     @http.route('/cruize_account/cruize_account/objects/<model("cruize_account.cruize_account"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cruize_account.object', {
#             'object': obj
#         })
