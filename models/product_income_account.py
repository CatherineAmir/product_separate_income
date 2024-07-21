from odoo import fields, models, api


class ProductIncomeAccount(models.Model):
    _inherit = 'product.income.account'

    is_sight_seeing = fields.Boolean('Is Sight Seeing',default=False)
    is_egyptian = fields.Boolean('Is Egyptian',default=False)
    is_base=fields.Boolean('Is Base',default=False)
