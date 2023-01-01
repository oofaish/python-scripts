import math
from datetime import date

import pytest
from dateutil.relativedelta import relativedelta

from asian_options import get_swap, turnbull_wakeman
from enums import OptionType
from helpers import time_to_maturity
from tests.helpers_test import EPSILON


def test_put_call_parity_for_asian_options():
    """Put-call parity."""
    pricing_date = date(2023, 2, 10)
    start_date = date(2023, 2, 1)
    end_date = start_date + relativedelta(months=1, days=-1)

    realized_value = 2200
    forward_value = 2300
    strike = 2250
    bullet_vol = 0.3
    r = 0.01

    call = turnbull_wakeman(
        OptionType.CALL,
        pricing_date,
        start_date,
        end_date,
        bullet_vol,
        forward_value,
        realized_value,
        strike,
        r,
    )
    put = turnbull_wakeman(
        OptionType.PUT,
        pricing_date,
        start_date,
        end_date,
        bullet_vol,
        forward_value,
        realized_value,
        strike,
        r,
    )

    swap = get_swap(forward_value, realized_value, pricing_date, start_date, end_date)
    t = time_to_maturity(pricing_date, end_date)

    portfolio = call - put
    forward = (swap - strike) * math.exp(-r * t)

    assert portfolio == pytest.approx(
        forward, EPSILON
    ), f"TW Call put parity failed {forward} != {portfolio} value"
