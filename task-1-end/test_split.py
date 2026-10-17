"""Unit tests for split.py."""

import argparse
import contextlib
import io
import unittest
from decimal import Decimal

from split import main, money, pays, positive_int, split_bill


class MoneyTests(unittest.TestCase):
    def test_parses_decimal(self):
        self.assertEqual(money("84.50"), Decimal("84.50"))

    def test_parses_whole_number(self):
        self.assertEqual(money("20"), Decimal("20"))

    def test_accepts_zero(self):
        self.assertEqual(money("0"), Decimal("0"))

    def test_rejects_non_number(self):
        with self.assertRaisesRegex(argparse.ArgumentTypeError, "not a number"):
            money("abc")

    def test_rejects_negative(self):
        with self.assertRaisesRegex(argparse.ArgumentTypeError, "zero or more"):
            money("-1")

    def test_rejects_non_finite(self):
        for value in ("inf", "-inf", "NaN"):
            with self.subTest(value=value):
                with self.assertRaises(argparse.ArgumentTypeError):
                    money(value)


class PositiveIntTests(unittest.TestCase):
    def test_parses_whole_number(self):
        self.assertEqual(positive_int("4"), 4)

    def test_accepts_one(self):
        self.assertEqual(positive_int("1"), 1)

    def test_rejects_zero(self):
        with self.assertRaisesRegex(argparse.ArgumentTypeError, "at least 1"):
            positive_int("0")

    def test_rejects_negative(self):
        with self.assertRaisesRegex(argparse.ArgumentTypeError, "at least 1"):
            positive_int("-3")

    def test_rejects_fraction(self):
        with self.assertRaisesRegex(argparse.ArgumentTypeError, "not a whole number"):
            positive_int("2.5")

    def test_rejects_text(self):
        with self.assertRaisesRegex(argparse.ArgumentTypeError, "not a whole number"):
            positive_int("two")


class SplitBillTests(unittest.TestCase):
    def test_even_split(self):
        tip, grand_total, shares = split_bill(Decimal("100"), Decimal("20"), 4)
        self.assertEqual(tip, Decimal("20.00"))
        self.assertEqual(grand_total, Decimal("120.00"))
        self.assertEqual(shares, [Decimal("30.00")] * 4)

    def test_leftover_cents_go_to_first_people(self):
        tip, grand_total, shares = split_bill(Decimal("10"), Decimal("0"), 3)
        self.assertEqual(grand_total, Decimal("10.00"))
        self.assertEqual(shares, [Decimal("3.34"), Decimal("3.33"), Decimal("3.33")])

    def test_shares_always_sum_to_grand_total(self):
        cases = [
            ("84.50", "18", 3),
            ("0.01", "0", 7),
            ("123.456", "17.5", 6),
            ("99.99", "15", 1),
        ]
        for total, tip_percent, people in cases:
            with self.subTest(total=total, tip=tip_percent, people=people):
                _, grand_total, shares = split_bill(
                    Decimal(total), Decimal(tip_percent), people)
                self.assertEqual(len(shares), people)
                self.assertEqual(sum(shares), grand_total)
                self.assertLessEqual(max(shares) - min(shares), Decimal("0.01"))

    def test_tip_rounds_half_up(self):
        # 10.10 * 5% = 0.505, which rounds up to 0.51.
        tip, grand_total, _ = split_bill(Decimal("10.10"), Decimal("5"), 1)
        self.assertEqual(tip, Decimal("0.51"))
        self.assertEqual(grand_total, Decimal("10.61"))

    def test_total_rounded_to_cent(self):
        tip, grand_total, shares = split_bill(Decimal("10.005"), Decimal("0"), 1)
        self.assertEqual(tip, Decimal("0.00"))
        self.assertEqual(grand_total, Decimal("10.01"))
        self.assertEqual(shares, [Decimal("10.01")])

    def test_zero_bill(self):
        tip, grand_total, shares = split_bill(Decimal("0"), Decimal("20"), 2)
        self.assertEqual(tip, Decimal("0.00"))
        self.assertEqual(grand_total, Decimal("0.00"))
        self.assertEqual(shares, [Decimal("0.00")] * 2)

    def test_more_people_than_cents(self):
        _, grand_total, shares = split_bill(Decimal("0.02"), Decimal("0"), 3)
        self.assertEqual(shares, [Decimal("0.01"), Decimal("0.01"), Decimal("0.00")])
        self.assertEqual(sum(shares), grand_total)


class PaysTests(unittest.TestCase):
    def test_singular(self):
        self.assertEqual(pays(1), "1 person pays")

    def test_plural(self):
        self.assertEqual(pays(3), "3 people pay")


class MainTests(unittest.TestCase):
    def run_main(self, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = main(argv)
        return code, out.getvalue()

    def test_even_split_output(self):
        code, output = self.run_main(["100", "20", "4"])
        self.assertEqual(code, 0)
        self.assertEqual(output, (
            "Bill:          100.00 USD\n"
            "Tip (20%):      20.00 USD\n"
            "Total:         120.00 USD\n"
            "\n"
            "Each of 4 pays 30.00 USD\n"
        ))

    def test_uneven_split_output(self):
        code, output = self.run_main(["10", "0", "3"])
        self.assertEqual(code, 0)
        self.assertIn(
            "1 person pays 3.34 USD, 2 people pay 3.33 USD (the cents don't divide evenly)",
            output)

    def test_currency_option_labels_every_amount(self):
        code, output = self.run_main(["100", "20", "4", "--currency", "EUR"])
        self.assertEqual(code, 0)
        self.assertNotIn("USD", output)
        self.assertEqual(output.count(" EUR\n"), 4)

    def test_invalid_arguments_exit_with_error(self):
        for argv in (["abc", "20", "4"], ["100", "-5", "4"], ["100", "20", "0"]):
            with self.subTest(argv=argv):
                with contextlib.redirect_stderr(io.StringIO()):
                    with self.assertRaises(SystemExit) as cm:
                        main(argv)
                self.assertEqual(cm.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
