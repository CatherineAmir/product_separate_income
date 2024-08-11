from odoo.tests.common import TransactionCase
from datetime import date
from math import floor


class TestCruise(TransactionCase):
    def setUp(self, *args, **kwargs):
        super(TestCruise, self).setUp()

        all_data = [
            # no sight seeing
            # EGP
            # 3 Night
            # No children
            # double Room

            {'nights': '3',
             'start_date': date(2024, 8, 1),
             'company_id': self.env.company.id,
             'state': 'draft',
             'cruise_lines': [(0, 0, {
                 'partner_id': 45,
                 'guest_name': 'Patric',
                 'guest_nationality': 78,
                 'cabinet_number': 1,
                 'cabinet_type': 'CABIN',
                 'occupancy': '2',
                 'sight_seeing': False,
                 'currency_id': 75,
                 'rate': 16000,
                 'payment_method': 'cash',

                 'children': '0'

             })],
             },

            # no sight seeing
            # EGP
            # 3 Night
            # 1 children
            # double Room

            {'nights': '3',
             'start_date': date(2024, 8, 1),
             'company_id': self.env.company.id,
             'state': 'draft',
             'cruise_lines': [(0, 0, {
                 'partner_id': 45,
                 'guest_name': 'Patric',
                 'guest_nationality': 78,
                 'cabinet_number': 1,
                 'cabinet_type': 'CABIN',
                 'occupancy': '2',
                 'sight_seeing': False,
                 'currency_id': 75,
                 'rate': 16000,
                 'payment_method': 'cash',

                 'children': '1',

             })],
             },

            # sight seeing
            # EGP
            # 3 Night
            # 1 children
            # double Room

            {'nights': '3',
             'start_date': date(2024, 8, 1),
             'company_id': self.env.company.id,
             'state': 'draft',
             'cruise_lines': [(0, 0, {
                 'partner_id': 45,
                 'guest_name': 'Patric',
                 'guest_nationality': 78,
                 'cabinet_number': 1,
                 'cabinet_type': 'CABIN',
                 'occupancy': '2',
                 'sight_seeing': True,
                 'currency_id': 75,
                 'rate': 16000,
                 'payment_method': 'cash',

                 'children': '1',

             })],
             },

            # sight seeing
            # EGP
            # 3 Night
            # 2 children
            # Triple Room

            {'nights': '3',
             'start_date': date(2024, 8, 1),
             'company_id': self.env.company.id,
             'state': 'draft',
             'cruise_lines': [(0, 0, {
                 'partner_id': 45,
                 'guest_name': 'Patric',
                 'guest_nationality': 78,
                 'cabinet_number': 1,
                 'cabinet_type': 'CABIN',
                 'occupancy': '3',
                 'sight_seeing': True,
                 'currency_id': 75,
                 'rate': 20000,
                 'payment_method': 'cash',
                 'children': '2',

             })],
             },

        ]

        self.cruises = self.env['cruise.cruise'].create(
            all_data)
        for cruise in self.cruises:
            cruise.confirm()
            cruise.create_invoices()



    def test_001_totals(self):
        for cruise in self.cruises:

            if len(cruise.cruise_lines) == 1 and len(cruise.invoice_ids) == 1:
                invoice_id =cruise.invoice_ids[0]
                total = (cruise.cruise_lines[0].cabinet_number *
                         int(cruise.nights) * cruise.cruise_lines[0].rate)
                self.assertAlmostEqual(invoice_id.amount_total_in_currency_signed, total,places=2)
                if invoice_id.amount_tax_signed:
                    print("amount",invoice_id.amount_total_in_currency_signed - invoice_id.amount_total_in_currency_signed / (
                                1.12 * 1.14),)
                    self.assertAlmostEqual(
                        invoice_id.amount_total_in_currency_signed - invoice_id.amount_total_in_currency_signed / (
                                1.12 * 1.14), invoice_id.amount_tax_signed,places=2)


                    self.assertAlmostEqual(invoice_id.amount_total_in_currency_signed / (1.12 * 1.14),
                                     invoice_id.amount_untaxed_signed,places=2)

    def test_002_quantities(self):
        for cruise in self.cruises:
            if len(cruise.cruise_lines) == 1 and len(cruise.invoice_ids) == 1:
                invoice_id = cruise.invoice_ids[0]
                mainline = invoice_id.invoice_line_ids.filtered(lambda line: line.main_line)
                all_lines = invoice_id.invoice_line_ids.filtered(lambda line: not line.main_line)
                line = cruise.cruise_lines[0]
                self.assertEqual(int(mainline.children), int(line.children))

                self.assertEqual(int(mainline.persons),
                             int(line.cabinet_number * (int(line.occupancy) + 0.5 * int(line.children))))

                self.assertEqual(int(mainline.quantity), int(mainline.cabinet_number) * int(mainline.nights))
                for line in all_lines:
                    if line.sight_seeing:
                        self.assertEqual(line.quantity, line.persons)
                    else:
                        self.assertEqual(line.quantity, mainline.persons * int(mainline.nights))



















