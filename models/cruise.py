from odoo import fields, models, api
from odoo.exceptions import ValidationError


class Cruise(models.Model):
    _name = 'cruise.cruise'
    _inherit=['mail.thread', 'mail.activity.mixin']
    _description = 'Cruise Trip'
    _rec_name='name'

    name = fields.Char(compute='_compute_name',store=1,string='Name',tracking=True)
    nights=fields.Selection([('3', '3'), ('4', '4'),('7','7')],default='3', string='Nights',tracking=True)
    start_date = fields.Date(string='Start Date',tracking=True,required=True)

    company_id=fields.Many2one('res.company', string='Company',default=lambda self: self.env.user.company_id)
    cruise_lines=fields.One2many('cruise.line','cruise_id',string="Cruise Line")

    state=fields.Selection([("draft","Draft"),("confirmed","Confirmed"),("cancelled","Cancelled")],default='draft',string='State',tracking=True)

    invoice_ids = fields.One2many('account.move','cruise_id', string="Invoices",readonly=1)
    invoice_line_ids = fields.Many2many('account.move.line')
    invoices_count=fields.Integer(string="Invoices Count",compute="compute_invoices")
    invoice_line_counts=fields.Integer(string="Lines",compute="compute_invoices")

    invoices_created=fields.Boolean(string="invoices_created")
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


    def create_invoices(self):
        cruise_lines=self.cruise_lines.read_group(domain=[],
                                                  fields=['id','partner_id','currency_id','guest_nationality','nights','cabinet_number','occupancy','sight_seeing','rate','is_paid_guide'
                                                                ],groupby=['partner_id','currency_id'],lazy=False)

        print("cruise_lines",len(cruise_lines))
        for line in cruise_lines:
            print('line..',line)
            currency_id=line['currency_id'][0]
            partner_id=line['partner_id'][0]
            lines = self.cruise_lines.filtered(
                lambda l: l.partner_id.id == partner_id and l.currency_id.id == currency_id)
            if not len(lines):
                continue
            invoice_id = self.env['account.move'].create({
                'partner_id': partner_id,
                'move_type': 'out_invoice',
                'currency_id': currency_id,
                'cruise_id': self.id,
                'invoice_date': self.start_date,

            })
            print('invoice_id',invoice_id)


            lines=self.cruise_lines.filtered(lambda l :l.partner_id.id==partner_id and l.currency_id.id==currency_id )
            print("lines",lines)
            invoice_lines=[]
            for l in lines:

                if not l.is_paid_guide:
                    product_id=self.env['product.product'].search([("product_tmpl_id.occupancy","=",l.occupancy),("categ_id.name","ilike","%Accomodation"),('name','not ilike','%guide%')])
                    print("product_id",product_id)

                else:
                    product_id = self.env['product.product'].search(
                        [("name","like","%guide%")])
                print("product_id", product_id.name)
                invoice_lines.append({
                    'product_id':product_id.id,
                    'quantity':int(self.nights)*l.cabinet_number,
                    'price_unit':l.rate,
                    'move_id':invoice_id.id,
                    'tax_ids':product_id.taxes_id,
                    'sight_seeing':l.sight_seeing

                })


            # print("invoice_lines",invoice_lines)
            self.env['account.move.line'].create(invoice_lines)

            # to do with and without sight visit


            # self.invoice_ids=invoice_ids
            self.invoice_line_ids=self.invoice_ids.mapped('line_ids').ids

    def compute_invoices(self):
        for record in self:
            record.invoices_count = len(record.invoice_ids)
            record.invoice_line_counts=len(set(record.invoice_line_ids))
            if record.invoices_count!=0:
                self.invoices_created=True
            else:
                self.invoices_created=False
    def action_view_invoices_ids(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "domain": [("id", "in", self.invoice_ids.ids)],
            "name": self.name,
            "view_mode": "tree,form",
            "context": {
                "default_cruise_id": self.id,

            },
        }
    def action_view_journal_items(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.move.line",
            "domain": [("id", "in", self.invoice_line_ids.ids)],
            "name": self.name,
            "view_mode": "tree,form",
            "context": {
                "default_group_by": "account_id",
            },
        }
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



