from datetime import date


def current_puzzle_year():
    # if it's on or after dec 1, use this year. Otherwise, use last year
    now = date.today()
    if now.month == 12:
        return str(now.year)
    return str(now.year - 1)
