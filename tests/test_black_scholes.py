import itertools
import math

import pytest

from black_scholes import calculate_black_scholes as bs
from enums import OptionType
from tests.helpers_test import EPSILON


def test_put_call_parity():
    """Put-call parity."""
    s = 100
    x = 120
    r = 0.02
    b = 0.01
    t = 0.7
    v = 0.2

    call = bs(OptionType.CALL, s, x, t, r, b, v).value
    put = bs(OptionType.PUT, s, x, t, r, b, v).value
    portfolio = call - put
    forward = s * math.exp((-r + b) * t) - x * math.exp(-r * t)
    assert portfolio == pytest.approx(
        forward, EPSILON
    ), f"Call put parity failed {forward} != {portfolio} value"


def test_zero_volatility_is_same_as_small_vol_price():
    r = 0.04
    b = 0.01
    t = 0.7
    v_zero = 0
    v_very_small = 1e-20
    pairings = itertools.product(
        [OptionType.CALL, OptionType.PUT], itertools.permutations([100, 120], 2)
    )
    print(pairings)
    for option_type, (strike, spot) in pairings:
        zero = bs(option_type, spot, strike, t, r, b, v_zero)
        very_small = bs(option_type, spot, strike, t, r, b, v_very_small)
        print(zero, very_small)
        assert zero.value == pytest.approx(very_small.value)
        assert zero.delta == pytest.approx(very_small.delta)
        assert zero.gamma == pytest.approx(very_small.gamma)
        assert zero.vega == pytest.approx(very_small.vega)
        assert zero.rho == pytest.approx(very_small.rho)
        assert zero.theta == pytest.approx(very_small.theta)
