#!/usr/bin/env python3
"""Split a bill, including tip, evenly between a number of people."""

import argparse
import sys
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

CENT = Decimal("0.01")


def money(value):
    """argparse type: a non-negative amount of money."""
    try:
        amount = Decimal(value)
    except InvalidOperation:
        raise argparse.ArgumentTypeError(f"not a number: {value!r}")
    if not amount.is_finite() or amount < 0:
        raise argparse.ArgumentTypeError(f"must be zero or more: {value!r}")
    return amount


def positive_int(value):
    """argparse type: a whole number of at least 1."""
    try:
        number = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"not a whole number: {value!r}")
    if number < 1:
        raise argparse.ArgumentTypeError(f"must be at least 1: {value!r}")
    return number


def currency_code(value):
    """argparse type: a non-empty currency label such as USD or EUR."""
    code = value.strip()
    if not code:
        raise argparse.ArgumentTypeError("must not be empty")
    return code


def split_bill(total, tip_percent, people):
    """Return (tip, grand_total, shares) with amounts rounded to the cent.

    Shares always add up exactly to grand_total: leftover cents go one
    each to the first people in the list.
    """
    tip = (total * tip_percent / 100).quantize(CENT, rounding=ROUND_HALF_UP)
    grand_total = total.quantize(CENT, rounding=ROUND_HALF_UP) + tip
    cents = int(grand_total / CENT)
    base, extra = divmod(cents, people)
    shares = [(base + (1 if i < extra else 0)) * CENT for i in range(people)]
    return tip, grand_total, shares


def pays(count):
    return "1 person pays" if count == 1 else f"{count} people pay"


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Split a bill, including tip, evenly between people.",
    )
    parser.add_argument("total", type=money, help="bill total before tip, e.g. 84.50")
    parser.add_argument("tip", type=money, help="tip percentage, e.g. 18 for 18%%")
    parser.add_argument("people", type=positive_int, help="number of people splitting")
    parser.add_argument("--currency", type=currency_code, default="USD", metavar="CODE",
                        help="currency shown next to every amount (default: USD)")
    args = parser.parse_args(argv)

    tip, grand_total, shares = split_bill(args.total, args.tip, args.people)
    cur = args.currency

    rows = [
        ("Bill", args.total.quantize(CENT, rounding=ROUND_HALF_UP)),
        (f"Tip ({args.tip}%)", tip),
        ("Total", grand_total),
    ]
    width = max(len(label) for label, _ in rows) + 1
    for label, amount in rows:
        print(f"{label + ':':<{width}} {amount:>10} {cur}")
    print()
    if len(set(shares)) == 1:
        print(f"Each of {args.people} pays {shares[0]} {cur}")
    else:
        high, low = shares[0], shares[-1]
        n_high = shares.count(high)
        print(f"{pays(n_high)} {high} {cur}, {pays(args.people - n_high)} {low} {cur} "
              f"(the cents don't divide evenly)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
