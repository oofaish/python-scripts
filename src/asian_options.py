from dataclasses import dataclass
from datetime import date
from math import exp, log, sqrt

from .black_scholes import calculate_black_scholes as bs
from .enums import OptionType
from .helpers import averaging_period, time_to_maturity


@dataclass
class TWResult:
    value: float
    vol: float


def floating_ratio(pricing_date: date, start_date: date, end_date: date) -> float:
    """
    tell me how much of the pricing period is still open, and how much of
    it has priced out already.
    """
    if pricing_date > end_date:
        return 0
    if start_date < pricing_date:
        total = (end_date - start_date).days + 1
        open_part = (end_date - pricing_date).days + 1

        return open_part / total

    return 1


def get_swap(forward: float, realized: float, pd: date, sd: date, ed: date) -> float:
    open_ratio = floating_ratio(pd, sd, ed)
    swap = open_ratio * forward + (1 - open_ratio) * realized
    return swap


def tw_m(bullet_vol: float, t_end: float, tau: float):
    if bullet_vol == 0:
        return 0
    if t_end == tau:
        return exp((bullet_vol**2) * t_end)

    m = (
        2 * exp((bullet_vol**2) * t_end)
        - 2 * exp((bullet_vol**2) * tau) * (1 + (bullet_vol**2) * (t_end - tau))
    ) / ((bullet_vol**4) * ((t_end - tau) ** 2))

    if m < 0:
        return 0

    return m


def tw_sigmaA(m: float, t_end: float) -> float:
    if m == 0:
        return 0
    if t_end <= 0:
        return 0

    return sqrt(log(m) / t_end)


def turnbull_wakeman(
    option_type: OptionType,
    pd: date,
    sd: date,
    ed: date,
    bullet_vol: float,
    forward: float,
    realized: float,
    strike: float,
    r: float = 0,
):
    """
    pricing options on commodity futures

    since we are pricing options on futures, we assume the cost of
    carry or the dividend yield is zero.

    notice we are ignore biz days/holidays for now, so assuming
    the index publishes every day.

    see http://www.espenhaug.com/AsianFuturesOptions.pdf for more details
    in the paper:
    t_start = Tau
    t_end = T
    t_averaging_period = T_2
    """
    swap = get_swap(forward, realized, pd, sd, ed)
    X = strike
    sigma = bullet_vol

    T_end = time_to_maturity(pd, ed)
    T_start = max(0, time_to_maturity(pd, sd))
    T_averaging_period = averaging_period(sd, ed)

    # notice how T_open_period is higher than T_end by an extra day
    # I believe if I want to see my option price and risk TODAY, I
    # want to assume that Vol for today is zero, but the price fix is not
    # in yet. So use T_end for BS pricing, but T_open_period for calculating
    # price ratios, etc
    T_open_period = min(T_averaging_period, averaging_period(pd, ed))

    if True:
        m = tw_m(sigma, T_end, T_start)
        v_asian = tw_sigmaA(m, T_end)

    if pd >= ed:
        X_HAT = X
        multiplier = 1
    elif pd > sd:
        X_HAT = (
            X * T_averaging_period / T_open_period
            - realized * (T_averaging_period - T_open_period) / T_open_period
        )

        if X_HAT > 0:
            swap = forward
            multiplier = T_open_period / T_averaging_period
        else:
            # CALL will definitely be exercised in this case since the only
            # way the final swap price will be less than STRIKE is if forward
            X_HAT = strike
            multiplier = 1
    else:
        X_HAT = X
        multiplier = 1
    value = bs(option_type, swap, X_HAT, T_end, r, 0, v_asian).value * multiplier
    return value
