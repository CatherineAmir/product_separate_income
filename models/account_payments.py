from odoo import fields, models, api


class Payment(models.Model):
    _inherit = ['account.payment']


    reconciled_invoice_ids = fields.Many2many('account.move', string="Reconciled Invoices",store=True)
    payment_state = fields.Selection([('deposit', "Deposit"), ("payment", "Payment")], string="Payment state",
                                     compute="_compute_payment_state", store=True)

    cruise_ids = fields.Many2many('cruise.cruise', string="Cruise_id",compute="_compute_cruise_ids",store=True,inverse='set_cruise_ids')
    cruise_boat_ids=fields.Many2many('cruise.boat', store=True,compute="_compute_cruise_boat_ids",inverse='_set_cruise_boat_ids')

    @api.depends('payment_type','has_reconciled_entries')
    def _compute_payment_state(self):
        for record in self:
            if record.has_reconciled_entries:
                record.payment_state = 'payment'
            else:
                record.payment_state = 'deposit'
    @api.depends('reconciled_invoice_ids.cruise_id')
    def _compute_cruise_ids(self):
        for record in self:
            if len(record.reconciled_invoice_ids):
                record.cruise_ids =record.reconciled_invoice_ids.mapped('cruise_id').ids

    def set_cruise_ids(self):
        for r in self:
            pass
    @api.depends('cruise_ids')
    def _compute_cruise_boat_ids(self):
        for r in  self:
            if r.cruise_ids:
                r.cruise_boat_ids =r.cruise_ids.mapped('cruise_boat_id').ids
    def _set_cruise_boat_ids(self):
        for r in self:
            pass