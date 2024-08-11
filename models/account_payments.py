from odoo import fields, models, api


class Payment(models.Model):
    _inherit = 'account.payment'

    reconciled_invoice_ids = fields.Many2many('account.move', string="Reconciled Invoices",store=True)

