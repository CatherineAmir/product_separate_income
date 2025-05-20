from odoo import fields, models, api
from odoo.exceptions import ValidationError


class Cruise(models.Model):
    _name = 'cruise.cruise'
    _inherit=['mail.thread', 'mail.activity.mixin', "analytic.mixin"]
    _description = 'Cruise Trip'
    _rec_name='name'

    name = fields.Char(compute='_compute_name',store=1,string='Name',tracking=True,inverse="_set_name",copy=False)
    # cruise_boat_idcruise_boat_id=fields.Selection([("Dahabia",'dahabia'),("Sun",'sun'),("Moon",'moon'),("Star","star"),("Nile",'nile')],default="Dahabia")
    cruise_boat_id=fields.Many2one("cruise.boat",string='Cruise Boat')
    nights=fields.Selection([('3', '3'), ('4', '4'),('7','7')],default='3', string='Nights',tracking=True)
    start_date = fields.Date(string='Start Date',tracking=True,required=True)

    company_id=fields.Many2one('res.company', string='Company',default=lambda self: self.env.user.company_id)
    cruise_lines=fields.One2many('cruise.line','cruise_id',string="Cruise Line",copy=True)

    state=fields.Selection([("draft","Draft"),("confirmed","Confirmed"),("cancelled","Cancelled")],default='draft',string='State',tracking=True)

    invoice_ids = fields.One2many('account.move','cruise_id', string="Invoices",readonly=1,copy=False)
    invoice_line_ids = fields.Many2many('account.move.line',copy=False)
    invoices_count=fields.Integer(string="Invoices Count",compute="compute_invoices")
    invoice_line_counts=fields.Integer(string="Lines",compute="compute_invoices")

    invoices_created=fields.Boolean(string="invoices_created")

    analytic_distribution = fields.Json(
        )



    @api.depends('start_date','cruise_boat_id')
    def _compute_name(self):
        for r in self:
            if r.start_date and r.cruise_boat_id:
                r.name= str(r.cruise_boat_id.name) + ' - ' + r.start_date.strftime('%d-%m-%Y')

    def _set_name(self):
        for r in self:
            pass
    def confirm(self):
        if len(self.cruise_lines):
            self.state="confirmed"
        else:
            raise ValidationError("You Can't confirm the Cruise With No Lines")


    def create_invoices(self):
        cruise_lines=self.cruise_lines.read_group(domain=[("cruise_id",'=',self.id)],
                                                  fields=['id','partner_id','currency_id','guest_nationality','nights','cabinet_number','occupancy','sight_seeing','rate','is_paid_guide','cruise_boat_id'
                                                                ],groupby=['partner_id','currency_id','cruise_boat_id'],lazy=False)

        print("cruise_lines",len(cruise_lines))
        for line in cruise_lines:
            print('line..',line)
            currency_id=line['currency_id'][0]
            partner_id=line['partner_id'][0]
            if line['cruise_boat_id']:
                cruise_boat_id=line['cruise_boat_id'][0]
                print("cruise_boat_id",cruise_boat_id)
            else:
                cruise_boat_id=self.cruise_boat_id.id
            lines = self.cruise_lines.filtered(
                lambda l: l.partner_id.id == partner_id and l.currency_id.id == currency_id and l.cruise_boat_id.id==cruise_boat_id)
            print("lines",lines)
            if not len(lines):
                continue
            invoice_id = self.env['account.move'].create({
                'partner_id': partner_id,
                'move_type': 'out_invoice',
                'currency_id': currency_id,
                'cruise_id': self.id,
                'invoice_date': self.start_date,
                'cruise_boat_id': cruise_boat_id,

            })
            print('invoice_id',invoice_id)


            lines=self.cruise_lines.filtered(lambda l :l.partner_id.id==partner_id and l.currency_id.id==currency_id and l.cruise_boat_id.id==cruise_boat_id )
            print("lines",lines)
            invoice_lines=[]
            for l in lines:

                if not l.is_paid_guide:
                    product_id=self.env['product.product'].search([("product_tmpl_id.occupancy","=",l.occupancy),("categ_id.name","ilike","%Accomodation")
                                                                      ,('name','not ilike','%guide%'),
                                                                      ("boat_id","=",cruise_boat_id)],limit=1)


                    print("product_id",product_id)

                else:
                    # print("guid")
                    product_id = self.env['product.product'].search(
                        [("name","ilike","%guide%"),("boat_id","=",cruise_boat_id)],limit=1)
                    print("product_id", product_id.name)
                # print('persons before',l.cabinet_number*(int(l.occupancy)+0.5*int(l.children)))
                # # print('l.cabinet_number',l.cabinet_number)
                # # print('(int(l.occupancy)',int(l.occupancy))
                # # print('(int(l.children)',int(l.children))
                # print('(int(l.occupancy)-0.5*int(l.children)',(int(l.occupancy)-0.5*int(l.children)))
                # print('persons',l.cabinet_number*(int(l.occupancy)-0.5*int(l.children)),)

                invoice_lines.append({
                    'product_id':product_id[0].id,
                    'quantity':int(l.nights)*l.cabinet_number,
                    'price_unit':l.rate,
                    'move_id':invoice_id.id,
                    'tax_ids':product_id.taxes_id,
                    'sight_seeing':l.sight_seeing,
                    'sight_seeing_price_person':l.sight_seeing_price_person,
                    'persons':l.cabinet_number*(int(l.occupancy)+0.5*int(l.children)),
                    'main_line':True,
                    'taken_line':False,
                    'default_unit_price':l.rate,
                    'default_quantity':int(l.nights)*l.cabinet_number,
                    'default_subtotal':l.rate*int(l.nights)*l.cabinet_number-(l.rate*int(self.nights)*l.cabinet_number*0.12*0.14),
                    'default_total':l.rate*int(l.nights)*l.cabinet_number,
                    'nights':l.nights,
                    'children':l.children,
                    'cabinet_number':l.cabinet_number,
                    'analytic_distribution':l.analytic_distribution,
                    "guest_nationality":l.guest_nationality.id,


                })


            # print("invoice_lines",invoice_lines)
            self.env['account.move.line'].create(invoice_lines)

            # to do with and without sight visit


            # self.invoice_ids=invoice_ids
            self.invoice_line_ids=self.invoice_ids.mapped('line_ids').ids
            print("self.invoice_line_ids_end ,",self.invoice_line_ids.read())

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
        domain=[("reconciled_invoice_ids", "in", self.invoice_ids.ids), ("state", '=', "posted"),
         ("payment_type", '=', 'inbound')]
        payment_journal_entry=self.env['account.payment'].search(domain).mapped("move_id")
        payment_journal_item=payment_journal_entry.mapped("line_ids").ids
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.move.line",
            "domain": [("id", "in", self.invoice_line_ids.ids+payment_journal_item)],
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
        return{
            "type":"ir.actions.act_window",
            "res_model": "account.analytic.line",
            "domain": [("move_line_id", "in", self.invoice_line_ids.ids+payment_journal_item)],
            "name": self.name,
            "view_mode": "tree,form",
            "context":{
                "group_by": "account_id"
            }
        }
    def action_view_payments(self):

        return{
            "type":"ir.actions.act_window",
            "res_model": "account.payment",
            "domain": [("reconciled_invoice_ids", "in", self.invoice_ids.ids),("state",'=',"posted"),("payment_type",'=','inbound')],
            "name": self.name,
            "view_mode": "tree,form",

        }

class CruiseLine(models.Model):
    _name = 'cruise.line'
    _inherit = ['mail.thread', 'mail.activity.mixin', "analytic.mixin"]

    cruise_id=fields.Many2one('cruise.cruise', string='Cruise',auto_join=True,tracking=True)
    partner_id=fields.Many2one('res.partner',string="Travel Agency",required=True,tracking=True,)
    guest_name=fields.Char(string="Guest Name",tracking=True,)
    guest_nationality=fields.Many2one('res.country',string="Guest Nationality",tracking=True,)
    checkin=fields.Date(string="Checkin date",related='cruise_id.start_date',store=True,tracking=True,)
    nights=fields.Selection([('3', '3'), ('4', '4'),('7','7')],compute='_compute_nights',store=1,tracking=True,inverse="_set_nights",)
    cabinet_number=fields.Integer(default=1)
    cabinet_type=fields.Selection([('CABIN UPGRADE TO SUITE',"cabin upgrade  to suite"),('CABIN',"cabin"),

                                 ("Other","other")],tracking=True,default="CABIN",store=True,)

    occupancy=fields.Selection([("1","SGL"),("2","DBL"),("3","TPL")],string="Occupancy",default="2",required=True)

    sight_seeing=fields.Boolean(default=False,string="Sight seeing")
    sight_seeing_lang=fields.Char(string="Sight Seeing Language",store=True)

    sight_seeing_price_person=fields.Float(string="Sight Seeing for Person in EGP",help="Sight Seeing for Person in EGP and include taxes(12-14%)")
    currency_id=fields.Many2one('res.currency',string="Currency",tracking=True,required=True)
    rate=fields.Monetary(string="Rate P/Unit/Night",tracking=True,required=True)
    payment_method=fields.Selection([('cash','Cash'),('cheque','Cheque'),("bank transfer","Bank Transfer")])
    boarding_number=fields.Char(string="")
    c_r_n=fields.Char(string="C/R N.")
    notes=fields.Char(string="Notes")

    is_paid_guide=fields.Boolean(string="Paid Guide",default=False)

    children=fields.Selection([('0','0'),('1','1'),('2','2')],default='0',string="Children")
    analytic_distribution = fields.Json(compute="_compute_analytic_distribution",store=True,inverse="_compute_dummy")
    # cruise_boat_id = fields.Selection(
    #     [("Dahabia", 'dahabia'), ("Sun", 'sun'), ("Moon", 'moon'), ("Star", "star"), ("Nile", 'nile')],
    #     default="Dahabia",compute="_compute_cruise_boat_id",store=True,inverse="_set_cruise_boat_id")
    cruise_boat_id=fields.Many2one('cruise.boat',string="Cruise Name",compute="_compute_cruise_boat_id",store=True,inverse="_set_cruise_boat_id")
    @api.depends('cruise_id.cruise_boat_id')
    def _compute_cruise_boat_id(self):
        for record in self:
            record.cruise_boat_id =record.cruise_id.cruise_boat_id.id
    def _set_cruise_boat_id(self):
       for r in self:
           pass
    @api.depends('cruise_id.nights')
    def _compute_nights(self):
        for line in self:
            line.nights=line.cruise_id.nights
    def _set_nights(self):
        for line in self:
            pass

    @api.depends('cruise_id.analytic_distribution')
    def _compute_analytic_distribution(self):
        for rec in self:
            rec.analytic_distribution=rec.cruise_id.analytic_distribution


    def _compute_dummy(self):
        for rec in self:
            pass




