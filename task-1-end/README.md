# Bill Splitter

`split.py` is a small command-line tool that adds a tip to a bill and splits the total evenly between people. It uses only the Python standard library (Python 3.8+).

## Usage

```
python3 split.py [--currency CODE] TOTAL TIP PEOPLE
```

| Argument | Meaning                         | Example |
|----------|---------------------------------|---------|
| `TOTAL`  | Bill total before tip           | `84.50` |
| `TIP`    | Tip percentage (`18` means 18%) | `18`    |
| `PEOPLE` | Number of people splitting      | `3`     |

| Option            | Meaning                                              | Example          |
|-------------------|------------------------------------------------------|------------------|
| `--currency CODE` | Currency shown next to every amount (default: `USD`) | `--currency EUR` |

Run `python3 split.py --help` to see the options.

## Examples

An even split:

```
$ python3 split.py 100 15 4
Bill:          100.00 USD
Tip (15%):      15.00 USD
Total:         115.00 USD

Each of 4 pays 28.75 USD
```

When the cents don't divide evenly, the leftover cents go to some of the people. The shares always add up to the exact total:

```
$ python3 split.py 84.50 18 3
Bill:           84.50 USD
Tip (18%):      15.21 USD
Total:          99.71 USD

2 people pay 33.24 USD, 1 person pays 33.23 USD (the cents don't divide evenly)
```

Use `--currency` to show a different currency. It only changes the label; no conversion is done:

```
$ python3 split.py 100 15 4 --currency EUR
Bill:          100.00 EUR
Tip (15%):      15.00 EUR
Total:         115.00 EUR

Each of 4 pays 28.75 EUR
```

Use a tip of `0` for no tip, and decimals for an exact percentage:

```
$ python3 split.py 60 0 2
$ python3 split.py 60 12.5 2
```

Invalid input prints an error and exits with status 2:

```
$ python3 split.py 50 20 0
usage: split.py [-h] [--currency CODE] total tip people
split.py: error: argument people: must be at least 1: '0'
```

## How the math works

- Amounts use `decimal.Decimal`, which avoids floating-point rounding errors.
- The tip is rounded to the nearest cent, with half a cent rounding up.
- The total is split by whole cents, so no cent is lost or invented.
