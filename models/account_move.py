from odoo import fields, models, api


class AccountMoveCruise(models.Model):
    _inherit = "account.move"

    cruise_id = fields.Many2one("cruise.cruise", string="Cruise")
    cruise_boat_id = fields.Many2one("cruise.boat", string='Cruise Boat')

    # cruise_name=fields.Selection(
    #     [("Dahabia", 'dahabia'), ("Sun", 'sun'), ("Moon", 'moon'), ("Star", "star"), ("Nile", 'nile')])

    def add_analytic_account(self):
        for move in self:
            analytics = list(
                move.invoice_line_ids.filtered(lambda line: line.main_line).mapped("analytic_distribution"))
            # print("analytics",analytics)
            # print("type_analytics",type(analytics))
            if len(analytics) == 1:
                for tax_line in move.line_ids.filtered(lambda x: x.display_type == "tax"):
                    tax_line.analytic_distribution = tax_line.analytic_distribution = analytics[0]


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    sight_seeing = fields.Boolean(string="is sight seeing?")
    sight_seeing_price_person = fields.Float(string="Sight Seeing for Person in EGP", )
    persons = fields.Float()
    nights = fields.Integer()
    main_line = fields.Boolean(default=False, copy=False)
    taken_line = fields.Boolean(default=False, copy=False)
    default_quantity = fields.Float(default=1, copy=False)
    default_unit_price = fields.Float(copy=False)
    default_subtotal = fields.Monetary(copy=False)
    default_total = fields.Monetary(copy=False)
    children = fields.Selection([('0', '0'), ('1', '1'), ('2', '2')], default='0', string="Children")
    cabinet_number = fields.Integer(default=1)
    guest_nationality = fields.Many2one('res.country', string="Guest Nationality", tracking=True, )
    # cruise_name = fields.Selection(related='move_id.cruise_name', string="cruise name",store=True)
    cruise_boat_id = fields.Many2one("cruise.boat", related="move_id.cruise_boat_id", string='Cruise Boat', store=True)
    cruise_id = fields.Many2one('cruise.cruise', string="Cruise ID", related='move_id.cruise_id', store=True)
    analytic_distribution = fields.Json(default=False)
    @api.constrains('product_id',
                    'account_id', 'price_unit', 'tax_ids')
    def split_account_lines(self):

        for r in self:

            if r.move_id.state != 'draft' or r.move_id.move_type not in ['out_invoice', 'out_refund']:
                return

            if r.product_id.product_tmpl_id.split_income_account \
                    and r.account_id.id == r.product_id.product_tmpl_id.property_account_income_id.id and not r.taken_line:

                total_taken = 0
                r.taken_line = True

                # print("persons_number",persons_number)

                # print("counter",0)
                counter = 0
                for account_line in r.product_id.product_tmpl_id.account_lines_ids:
                    counter += 1
                    # print('r.persons',r.persons)

                    if account_line.separation_criteria == 'percentage':

                        total_taken += r.price_unit * account_line.percentage_amount
                        qty = r.persons * r.nights
                        print("r.analytic_distribution", r.analytic_distribution)
                        vals = {
                            'account_id': account_line.income_account_id.id,

                            'debit': (r.debit * account_line.percentage_amount),
                            'credit': (r.credit * account_line.percentage_amount),
                            'name': account_line.label,
                            'move_id': r.move_id.id,
                            'price_unit': (r.price_unit * account_line.percentage_amount),
                            'quantity': qty,
                            "analytic_distribution": r.analytic_distribution,

                        }

                        if account_line.is_base:
                            r.with_context(check_move_validity=False).write(vals)
                        else:
                            r.move_id.with_context(check_move_validity=False)
                            new_line = r.copy(vals)
                            new_line.with_context(check_move_validity=False).write(vals)
                            r.with_context(check_move_validity=True)


                    else:
                        amount_line = account_line.fixed_amount
                        if not r.sight_seeing and account_line.is_sight_seeing:
                            continue
                        if account_line.is_sight_seeing:
                            sight_seeing = True
                            qty = r.persons
                            if r.sight_seeing_price_person:
                                amount_line = r.sight_seeing_price_person

                            # print("qty sight seeing", qty)
                            if r.guest_nationality.id == 65 or not r.guest_nationality:
                                if account_line.is_egyptian:
                                    pass
                                else:
                                    continue
                            else:
                                if account_line.is_egyptian:
                                    continue
                                else:
                                    pass
                        else:
                            sight_seeing = False
                            # print("quatinty", r.quantity)
                            # print("persons", r.persons)
                            qty = r.persons * r.nights
                            # print("qty not sight seeing", qty)

                        rate = r.currency_rate

                        total_taken += (account_line.fixed_amount * qty)

                        vals = {
                            'account_id': account_line.income_account_id.id,
                            'name': account_line.label,
                            'move_id': r.move_id.id,
                            'price_unit': amount_line * rate,
                            'quantity': qty,
                            'sight_seeing': sight_seeing,
                            "analytic_distribution": r.analytic_distribution,
                        }
                        # print("account_line.fixed_amount*rate",account_line.fixed_amount*rate)
                        print("vals fixed", vals)

                        if account_line.is_base:

                            # print("total_taken baseeee>>>",total_taken)
                            all_remaining = (r.price_unit * r.quantity / rate) - total_taken

                            one_remaining = all_remaining * rate / (r.quantity)

                            vals = {
                                'account_id': account_line.income_account_id.id,

                                'debit': all_remaining if r.debit else 0,
                                'credit': all_remaining if r.credit else 0,
                                'name': r.name,
                                'move_id': r.move_id.id,
                                'price_unit': one_remaining,
                                'quantity': r.quantity,
                                "analytic_distribution": r.analytic_distribution,
                            }

                            r.with_context(check_move_validity=False).update(vals)



                        else:

                            r.move_id.with_context(check_move_validity=False)
                            new_line = r.copy(vals)
                            new_line.with_context(check_move_validity=False).write(vals)

            r.move_id.add_analytic_account()
