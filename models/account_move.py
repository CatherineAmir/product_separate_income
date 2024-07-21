from odoo import fields, models, api


class AccountMove(models.Model):
   _inherit='account.move.line'

   @api.constrains('product_id','account_id')
   def split_account_lines(self):

      for r in self:
         if r.move_id.state!='draft':
            return

         if r.product_id.product_tmpl_id.split_income_account \
                 and r.account_id.id==r.product_id.product_tmpl_id.property_account_income_id.id:

            for account_line in r.product_id.product_tmpl_id.account_lines_ids:
               if account_line.separation_criteria=='percentage':

                  vals={
                     'account_id':account_line.income_account_id.id,
                     'amount_currency':(r.amount_currency*account_line.percentage_amount),
                     'debit':(r.debit*account_line.percentage_amount),
                     'credit':(r.credit*account_line.percentage_amount),
                     'name':account_line.label,
                     'move_id':r.move_id.id,
                     'price_unit': (r.price_unit*account_line.percentage_account),
                     'price_subtotal': (r.price_subtotal*account_line.percentage_account),
                     # 'price_total': (r.price_total-r.price_subtotal**account_line.percentage_account)+
                  }

               else:
                  vals = {
                     'account_id': account_line.income_account_id.id,
                     'amount_currency': (account_line.fixed_amount),
                     'debit': account_line.fixed_amount if r.debit else 0 ,
                     'credit': account_line.fixed_amount if r.credit else 0,
                     'name': account_line.label,
                     'move_id': r.move_id.id,
                     'price_unit': (r.price_unit * account_line.percentage_account),
                     'price_subtotal': (r.price_subtotal * account_line.percentage_account),
                     # 'price_total': (r.price_total-r.price_subtotal**account_line.percentage_account)+
                  }



               if account_line==r.product_id.product_tmpl_id.categ_id.account_lines_ids[-1]:

                  r.with_context(check_move_validity=False).write(vals)



               else:

                  r.move_id.with_context(check_move_validity=False)
                  new_line = r.copy(vals)
                  new_line.with_context(check_move_validity=False).write(vals)




               r.with_context(check_move_validity=True)

