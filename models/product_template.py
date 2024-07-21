from odoo import fields, models, api


class ProductTemplate(models.Model):
   _inherit='product.template'
   occupancy = fields.Selection([("1", "SGL"), ("2", "DBL"), ("3", "TPL")], string="Occupancy", default="2")

