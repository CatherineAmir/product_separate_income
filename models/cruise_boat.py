from odoo import fields, models, api


class CruiseBoat(models.Model):
    _name = 'cruise.boat'
    _inherit=['mail.thread','analytic.mixin','mail.activity.mixin']
    _description = 'Description'
    _rec_name = 'name'

    name = fields.Char(string="Boat Name",required=True)

    cruise_ids = fields.One2many('cruise.cruise','cruise_boat_id',string="Cruise_ids")
    cruise_count = fields.Integer(string='Cruises',compute='_compute_cruises_numbers')

    cruise_lines=fields.One2many('cruise.line','cruise_boat_id')

    product_ids=fields.One2many('product.template','boat_id')
    product_count=fields.Integer(compute='_compute_product_count')

    transfer_ids=fields.One2many('stock.picking','boat_id')
    transfer_count=fields.Integer(compute='_compute_transfer_count')

    invoice_ids = fields.One2many('account.move', 'cruise_boat_id', string="Invoices", readonly=1, copy=False)
    invoice_line_ids = fields.One2many('account.move.line','cruise_boat_id')
    invoices_count = fields.Integer(string="Invoices Count", compute="compute_invoices")
    invoice_line_counts = fields.Integer(string="Lines", compute="compute_invoices")
    @api.depends('invoice_ids')
    def compute_invoices(self):
        for record in self:
            record.invoices_count = len(record.invoice_ids)
            record.invoice_line_counts = len(set(record.invoice_line_ids))
    @api.depends('transfer_ids')
    def _compute_transfer_count(self):
        for boat in self:
            boat.transfer_count=len(boat.transfer_ids)
    @api.depends('cruise_ids')
    def _compute_cruises_numbers(self):
        for boat in self:
            boat.cruise_count = len(boat.cruise_ids)


    @api.depends('product_ids')
    def _compute_product_count(self):
        for boat in self:
            boat.product_count = len(boat.product_ids)
    def action_view_cruises(self):
        action={
          "type":'ir.actions.act_window',
          "res_model":"cruise.cruise",
          "domain":[("cruise_boat_id","=",self.id)],
          "name":self.name,
          "view_mode":"tree,form"
        }
        return action

    def action_view_cruise_lines(self):
        action={
            "type":'ir.actions.act_window',
            "res_model":"cruise.line",
            "domain":[("cruise_boat_id","=",self.id)],
            "name":self.name,
            "view_mode":"tree,form",
            "context":{
                    "group_by":"cruise_id"}
        }
        return action
    def action_view_products(self):
        action={
            "type":'ir.actions.act_window',
            "res_model":"product.template",
            "domain":[("boat_id","=",self.id)],
            "name":self.name,
            "view_mode":"tree,form",

        }
        return action
    def action_view_transfers(self):
        action={
            "type":'ir.actions.act_window',
            "res_model":"stock.picking",
            "domain":[("boat_id","=",self.id)],
            "name":self.name,
            "view_mode":"tree,form",

        }
        return action

    def action_view_invoices_ids(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "domain": [("id", "in", self.invoice_ids.ids)],
            "name": self.name,
            "view_mode": "tree,form",
            "context": {
                "default_cruise_boat_id": self.id,

            },
        }


    def action_view_journal_items(self):
        domain = [("reconciled_invoice_ids", "in", self.invoice_ids.ids), ("state", '=', "posted"),
                  ("payment_type", '=', 'inbound')]
        payment_journal_entry = self.env['account.payment'].search(domain).mapped("move_id")
        payment_journal_item = payment_journal_entry.mapped("line_ids").ids
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.move.line",
            "domain": [("id", "in", self.invoice_line_ids.ids + payment_journal_item)],
            "name": self.name,
            "view_mode": "tree,form",
            "context": {
                "group_by": "account_id",
            },
        }

    def action_view_analytic_lines(self):
        domain = [("reconciled_invoice_ids", "in", self.invoice_ids.ids), ("state", '=', "posted"),
                  ("payment_type", '=', 'inbound')]
        payment_journal_entry = self.env['account.payment'].search(domain).mapped("move_id")
        payment_journal_item = payment_journal_entry.mapped("line_ids").ids
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.analytic.line",
            "domain": [("move_line_id", "in", self.invoice_line_ids.ids + payment_journal_item)],
            "name": self.name,
            "view_mode": "tree,form",
            "context": {
                "group_by": "account_id"
            }
        }

    def action_view_payments(self):

        return {
            "type": "ir.actions.act_window",
            "res_model": "account.payment",
            "domain": [("reconciled_invoice_ids", "in", self.invoice_ids.ids), ("state", '=', "posted"),
                       ("payment_type", '=', 'inbound')],
            "name": self.name,
            "view_mode": "tree,form",

        }
