from odoo import fields, models, api


class AccountPaymentRegister(models.TransientModel):
    _inherit=['account.payment.register']
    # _inherits = {: 'analytic_precision'}

    _description = 'Description'

    cruise_ids = fields.Many2many('cruise.cruise', string="Cruise_id", compute="_compute_cruise_ids", store=True,
                                  inverse='set_cruise_ids')
    cruise_boat_ids = fields.Many2many('cruise.boat', store=True, compute="_compute_cruise_ids",
                                       inverse='set_cruise_ids')
    analytic_distribution = fields.Json()

    analytic_precision = fields.Integer(
        store=False,
        default=lambda self: self.env['decimal.precision'].precision_get("Percentage Analytic"),
    )

    @api.depends('line_ids')
    def _compute_cruise_ids(self):
        for r in self:
            r.cruise_ids =r.line_ids.mapped('cruise_id').ids
            r.cruise_boat_ids =r.line_ids.mapped('cruise_boat_id').ids

    def set_cruise_ids (self):
        for r in self:
            pass


    def _create_payment_vals_from_wizard(self,batch_result):
        payment_vals=super(AccountPaymentRegister,self)._create_payment_vals_from_wizard(batch_result)
        payment_vals["cruise_boat_ids"] = self.cruise_boat_ids.ids
        payment_vals["cruise_ids"]=self.cruise_ids.ids
        payment_vals['analytic_distribution']=self.analytic_distribution
        return payment_vals