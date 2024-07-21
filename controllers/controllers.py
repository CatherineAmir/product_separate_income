# -*- coding: utf-8 -*-
# from odoo import http


# class ServiceProductPackage(http.Controller):
#     @http.route('/service_product_package/service_product_package', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/service_product_package/service_product_package/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('service_product_package.listing', {
#             'root': '/service_product_package/service_product_package',
#             'objects': http.request.env['service_product_package.service_product_package'].search([]),
#         })

#     @http.route('/service_product_package/service_product_package/objects/<model("service_product_package.service_product_package"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('service_product_package.object', {
#             'object': obj
#         })
