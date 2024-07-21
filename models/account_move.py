from odoo import fields, models, api



class AccountMove(models.Model):
    _inherit = 'account.move.line'

    @api.constrains('product_id', 'account_id')
    def split_account_lines(self):
        for r in self:

            if r.move_id.state != 'draft' or r.move_id.move_type=='entry':
                return
            print("r.account_id.id",r.account_id.id)
            print("r.product_id.product_tmpl_id.property_account_income_id.id",r.product_id.product_tmpl_id.property_account_income_id.id)
            if r.product_id.product_tmpl_id.split_income_account \
                    and r.account_id.id == r.product_id.product_tmpl_id.property_account_income_id.id:
                print("heerrrrr")
                total_taken=0
                persons_number=int(r.product_id.product_tmpl_id.occupancy)
                print("persons_number",persons_number)

                print("counter",0)
                counter=0
                for account_line in r.product_id.product_tmpl_id.account_lines_ids:
                    counter+=1
                    if account_line.separation_criteria == 'percentage':
                        print("percentage")

                        total_taken += r.price_unit * account_line.percentage_amount
                        print("total_taken",total_taken)
                        vals = {
                            'account_id': account_line.income_account_id.id,

                            'debit': (r.debit * account_line.percentage_amount),
                            'credit': (r.credit * account_line.percentage_amount),
                            'name': account_line.label,
                            'move_id': r.move_id.id,
                            'price_unit': (r.price_unit * account_line.percentage_amount),
                            'quantity': account_line.quantity,

                        }
                        print("vals percenatge",vals)

                    else:
                        if account_line.is_sight_seeing:
                            qty=1
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
                        rate = r.currency_rate
                        print("total_taken fixed after", total_taken)
                        print("is_sight_seeing",account_line.is_sight_seeing)
                        print("qty",qty)
                        print("account_line.fixed_amount",account_line.fixed_amount)
                        print("persons_number",persons_number)
                        total_taken += (account_line.fixed_amount*qty*persons_number)
                        print("total_taken fixed after",total_taken)
                        # print("account_line.fixed_amount*qty",account_line.fixed_amount*qty)

                        print("rate",rate)
                        vals = {
                            'account_id': account_line.income_account_id.id,

                            'debit': account_line.fixed_amount*qty*persons_number if r.debit else 0,
                            'credit': account_line.fixed_amount*qty*persons_number if r.credit else 0,
                            'name': account_line.label,
                            'move_id': r.move_id.id,
                            'price_unit': account_line.fixed_amount*rate,

                            'quantity': qty*persons_number
                        }
                        print("vals fixed",vals)

                    if account_line.is_base:
                        # total_taken = total_taken - account_line
                        print("total_taken baseeee>>>",total_taken)
                        all_remaining=(r.price_unit*r.quantity/rate)-total_taken

                        one_remaining=all_remaining*rate/(r.quantity)

                        print("all_remaining",all_remaining)
                        print("one_remaining",one_remaining)

                        vals = {
                            'account_id': account_line.income_account_id.id,
                            # 'amount_currency':all_remaining ,
                            'debit': all_remaining if r.debit else 0,
                            'credit': all_remaining if r.credit else 0,
                            'name': r.name,
                            'move_id': r.move_id.id,
                            'price_unit': one_remaining,
                            'quantity': r.quantity,
                        }
                        print("vals in update",vals)

                        r.with_context(check_move_validity=False).update(vals)



                    else:

                        r.move_id.with_context(check_move_validity=False)
                        new_line = r.copy(vals)
                        new_line.with_context(check_move_validity=False).write(vals)



                    # if list(set(r.product_id.product_tmpl_id.account_lines_ids.
                    #                     mapped("separation_criteria")))[0] == 'fixed':
                    #     # r.with_context(check_move_validity=True)
                    #


                print("counter at the end>>>",counter)





