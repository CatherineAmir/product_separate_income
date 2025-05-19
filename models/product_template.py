from odoo import fields, models, api


class ProductTemplate(models.Model):
   _inherit='product.template'
   occupancy = fields.Selection([("1", "SGL"), ("2", "DBL"), ("3", "TPL")], string="Occupancy", default="2")
   merge_product=fields.Boolean(string="Merge Product" ,default=False)
   boat_id=fields.Many2one('cruise.boat', string="Boat")


class ProductProduct(models.Model):
   _inherit = 'product.product'

   boat_id=fields.Many2one('cruise.boat',related='product_tmpl_id.boat_id', string="Boat")

