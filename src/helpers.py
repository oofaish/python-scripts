from datetime import date


def time_to_maturity(pricing_date: date, this_date: date) -> float:
    """
    Calculate time to maturity in years.
    Notice how we dont add a + 1 here.
    If an option is expiring today, time to maturity is 0.
    Tomorrow, it is 1/365, and so on.
    """
    return ((this_date - pricing_date).days) / 365


def averaging_period(start_date: date, end_date: date) -> float:
    """
    When looking at the averaging period of an Asian option
    though, we want to include the day of expiry in the averaging
    period.
    """
    return ((end_date - start_date).days + 1) / 365
