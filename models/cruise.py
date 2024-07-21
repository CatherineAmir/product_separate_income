from odoo import fields, models, api
from odoo.exceptions import ValidationError


class Cruise(models.Model):
    _name = 'cruise.cruise'
    _inherit=['mail.thread', 'mail.activity.mixin']
    _description = 'Cruise Trip'

    name = fields.Char(compute='_compute_name',store=1,string='Name',tracking=True)
    nights=fields.Selection([('3', '3'), ('4', '4'),('7','7')],default='3', string='Nights',tracking=True)
    start_date = fields.Date(string='Start Date',tracking=True,required=True)

    company_id=fields.Many2one('res.company', string='Company',default=lambda self: self.env.user.company_id)
    cruise_lines=fields.One2many('cruise.line','cruise_id',string="Cruise Line")

    state=fields.Selection([("draft","Draft"),("confirmed","Confirmed"),("cancelled","Cancelled")],default='draft',string='State',tracking=True)


    @api.depends('start_date','company_id')
    def _compute_name(self):
        for r in self:
            if r.start_date and r.company_id:
                r.name= str(r.company_id.name) + ' - ' + r.start_date.strftime('%d-%m-%Y')


    def confirm(self):
        if len(self.cruise_lines):
            self.state="confirmed"
        else:
            raise ValidationError("You Can't confirm the Cruise With No Lines")


    def create_journal_entry(self):
        for line in self.cruise_lines:
            pass



class CruiseLine(models.Model):
    _name = 'cruise.line'

    cruise_id=fields.Many2one('cruise.cruise', string='Cruise',autojoin=True,tracking=True)
    partner_id=fields.Many2one('res.partner',string="Travel Agency",required=True,tracking=True,)
    guest_name=fields.Char(string="Guest Name",tracking=True,)
    guest_nationality=fields.Many2one('res.country',string="Guest Nationality",tracking=True,)
    checkin=fields.Date(string="Checkin date",related='cruise_id.start_date',store=True,tracking=True,)
    nights=fields.Selection(related='cruise_id.nights',store=1,tracking=True,)
    cabinet_number=fields.Integer(default=1)
    cabinet_type=fields.Selection([('CABIN UPGRADE TO SUITE',"cabin upgrade  to suite"),('CABIN',"cabin"),

                                 ("Other","other")],tracking=True,)

    occupancy=fields.Selection([("1","SGL"),("2","DBL"),("3","TPL")],string="Occupancy",default="2",required=True)

    sight_seeing=fields.Boolean(default=False,string="Sight seeing")
    sight_seeing_lang=fields.Char(string="Sight Seeing Language",store=True)

    currency_id=fields.Many2one('res.currency',string="Currency",tracking=True)
    rate=fields.Monetary(string="Rate P/Unit/Night",tracking=True,required=True)
    payment_method=fields.Selection([('cash','Cash'),('cheque','Cheque'),("bank transfer","Bank Transfer")])
    boarding_number=fields.Char(string="")
    c_r_n=fields.Char(string="C/R N.")
    notes=fields.Char(string="Notes")

    is_paid_guide=fields.Boolean(string="Paid Guide",default=False)