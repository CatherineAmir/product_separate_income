from odoo import fields, models, api,_
from odoo.exceptions import ValidationError
ACCOUNT_DOMAIN = "['&', '&', '&', ('deprecated', '=', False), ('account_type', 'not in', ('asset_receivable','liability_payable','asset_cash','liability_credit_card')), ('company_id', '=', current_company_id), ('is_off_balance', '=', False)]"
class ProductTemlate(models.Model):
    _inherit="product.template"

    split_income_account=fields.Boolean(string="Split Income Account",copy=True)
    account_lines_ids=fields.One2many('product.income.account','product_template_id',copy=True)
    # @api.constrains('account_lines_ids')
    # def account_lines(self):
    #     for record in self:
    #         if record.account_lines_ids:
    #             if sum(record.account_lines_ids.mapped('percentage_amount'))!=1.00 :
    #                 raise ValidationError(_("Account lines Percentage must equal 100"))




class ProductIncomeAccount(models.Model):
    _name='product.income.account'

    product_template_id=fields.Many2one('product.template',string="Product",auto_join=True,ondelete="cascade")
    income_account_id=fields.Many2one('account.account',string="Income account",requried=1,domain=ACCOUNT_DOMAIN)

    separation_criteria=fields.Selection([('percentage', 'Percentage'), ("fixed" ,"Fixed")],default="fixed",required=True)
    percentage_amount=fields.Float(string="Percentage Amount")
    fixed_amount=fields.Float(string="Fixed Amount")
    label=fields.Char(string="Label",required=True)

