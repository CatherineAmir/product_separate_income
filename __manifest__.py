# -*- coding: utf-8 -*-
{
    'name': "cruise_account",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Sita-Egypt",
    'website': "https://Sita-eg.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','product','account','mail','service_product_package','stock','stock_account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/cruise_line.xml',
        'views/cruise_view.xml',
        'views/cruise_boat_view.xml',
        'views/product_template.xml',
        'views/account_move.xml',
        'views/payments.xml',
        'reports/invoice_product_merged.xml',
        'wizards/payment_register.xml',
        'views/stock_picking.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
