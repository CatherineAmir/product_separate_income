from odoo import fields, models, api

class AccountMove(models.Model):
    _inherit = "account.move"

    cruise_id=fields.Many2one("cruise.cruise", string="Cruise")


class AccountMove(models.Model):
    _inherit = 'account.move.line'
    sight_seeing=fields.Boolean(string="is sight seeing?")
    persons=fields.Integer(default=1)
    main_line=fields.Boolean(default=False,copy=False)
    taken_line=fields.Boolean(default=False,copy=False)
    default_quantity=fields.Float(default=1,copy=False)
    default_unit_price=fields.Float(copy=False)
    default_subtotal=fields.Monetary(copy=False)
    default_total=fields.Monetary(copy=False)

    @api.constrains('product_id', 'account_id','price_unit','tax_ids')
    def split_account_lines(self):
        for r in self:

            if r.move_id.state != 'draft' or r.move_id.move_type=='entry':
                return
            # print("r.account_id.id",r.account_id.id)
            # print("r.product_id.product_tmpl_id.property_account_income_id.id",r.product_id.product_tmpl_id.property_account_income_id.id)
            if r.product_id.product_tmpl_id.split_income_account \
                    and r.account_id.id == r.product_id.product_tmpl_id.property_account_income_id.id and not r.taken_line:
                # print("heerrrrr")
                total_taken=0
                r.taken_line=True
                persons_number=int(r.product_id.product_tmpl_id.occupancy)
                # print("persons_number",persons_number)

                # print("counter",0)
                counter=0
                for account_line in r.product_id.product_tmpl_id.account_lines_ids:
                    counter+=1
                    if account_line.separation_criteria == 'percentage':


                        total_taken += r.price_unit * account_line.percentage_amount

                        vals = {
                            'account_id': account_line.income_account_id.id,

                            'debit': (r.debit * account_line.percentage_amount),
                            'credit': (r.credit * account_line.percentage_amount),
                            'name': account_line.label,
                            'move_id': r.move_id.id,
                            'price_unit': (r.price_unit * account_line.percentage_amount),
                            'quantity': account_line.quantity,

                        }


                    else:
                        if not r.sight_seeing and account_line.is_sight_seeing:
                            continue
                        if account_line.is_sight_seeing:
                            qty=r.persons
                            print("qty sight seeing",qty)
                            if r.move_id.currency_id.id == r.move_id.company_id.currency_id.id:
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
                            qty=r.quantity
                        # rate = round(r.currency_rate,4)
                        rate=r.currency_rate
                        # print("total_taken fixed after", total_taken)
                        # print("is_sight_seeing",account_line.is_sight_seeing)
                        # print("qty",qty)
                        # print("account_line.fixed_amount",account_line.fixed_amount)
                        # print("persons_number",persons_number)
                        total_taken += (account_line.fixed_amount*qty*persons_number)
                        # print("total_taken fixed after",total_taken)
                        # print("account_line.fixed_amount*qty",account_line.fixed_amount*qty)

                        # print("rate",rate)
                        vals = {
                            'account_id': account_line.income_account_id.id,

                            'debit': account_line.fixed_amount*qty*persons_number if r.debit else 0,
                            'credit': account_line.fixed_amount*qty*persons_number if r.credit else 0,
                            'name': account_line.label,
                            'move_id': r.move_id.id,
                            'price_unit': account_line.fixed_amount*rate,

                            'quantity': qty*persons_number
                        }
                        # print("account_line.fixed_amount*rate",account_line.fixed_amount*rate)
                        # print("vals fixed",vals)

                    if account_line.is_base:

                        # print("total_taken baseeee>>>",total_taken)
                        all_remaining=(r.price_unit*r.quantity/rate)-total_taken

                        one_remaining=all_remaining*rate/(r.quantity)

                        # print("all_remaining",all_remaining)
                        # print("one_remaining",one_remaining)

                        vals = {
                            'account_id': account_line.income_account_id.id,

                                'debit': all_remaining if r.debit else 0,
                            'credit': all_remaining if r.credit else 0,
                            'name': r.name,
                            'move_id': r.move_id.id,
                            'price_unit': one_remaining,
                            'quantity': r.quantity,
                        }
                        # print("vals in update",vals)

                        r.with_context(check_move_validity=False).update(vals)



                    else:
                        # try:

                            r.move_id.with_context(check_move_validity=False)
                            new_line = r.copy(vals)
                            new_line.with_context(check_move_validity=False).write(vals)

                        # except:
                        #     r.move_id.with_context(check_move_validity=False)
                        #     new_line.with_context(check_move_validity=False).write(vals)






