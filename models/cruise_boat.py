from odoo import fields, models, api


class CruiseBoat(models.Model):
    _name = 'cruise.boat'
    _description = 'Description'

    name = fields.Char(string="Cruise Name",required=True)
