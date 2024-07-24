from odoo import fields, models, api


class Report(models.AbstractModel):
    _name = 'report.cruise_account.invoice_printout_merged'

    _description = 'Account report with payment lines'
    _inherit = 'report.account.report_invoice'



    @api.model
    def _get_report_values(self, docids, data=None):
        print("docids",docids)
        print("data",data)
        # lines =
        # return {
        #     'lines': lines,
        # }

