import math
from dataclasses import dataclass

from scipy.stats import norm

from .enums import OptionType


@dataclass
class BSResult:
    value: float
    delta: float
    gamma: float
    theta: float
    vega: float
    rho: float


def calculate_black_scholes(
    option_type: OptionType, s: float, x: float, t: float, r: float, b: float, v: float
) -> float:
    """Price an option using the Black-Scholes model.
    option_type: OptionType.CALL or OptionType.PUT
    s: spot price
    x: strike price
    t: expiration time
    r: risk-free rate
    b: cost of carry
    v: volatility
    """
    if option_type not in [OptionType.CALL, OptionType.PUT]:
        raise ValueError(
            f"Unknown option type: {option_type} (must be OptionType.CALL or OptionType.PUT)"
        )

    if t <= 0 or v == 0:
        cp = option_type.value
        value = max(0, cp * (s * math.exp((-r + b) * t) - x * math.exp(-r * t)))
        delta = cp * math.exp((b - r) * t) if value > 0 else 0
        gamma = 0
        theta = (
            -cp * ((b - r) * s * math.exp((b - r) * t) - -r * x * math.exp(-r * t))
            if value > 0
            else 0
        )
        vega = 0
        rho = cp * x * t * math.exp(-r * t) if value > 0 else 0
        return BSResult(value, delta, gamma, theta, vega, rho)

    t__sqrt = math.sqrt(t)

    d1 = (math.log(s / x) + (b + (v * v) / 2) * t) / (v * t__sqrt)
    d2 = d1 - v * t__sqrt

    if option_type == OptionType.CALL:
        value = s * math.exp((b - r) * t) * norm.cdf(d1) - x * math.exp(
            -r * t
        ) * norm.cdf(d2)
        delta = math.exp((b - r) * t) * norm.cdf(d1)
        gamma = math.exp((b - r) * t) * norm.pdf(d1) / (s * v * t__sqrt)
        theta = (
            -(s * v * math.exp((b - r) * t) * norm.pdf(d1)) / (2 * t__sqrt)
            - (b - r) * s * math.exp((b - r) * t) * norm.cdf(d1)
            - r * x * math.exp(-r * t) * norm.cdf(d2)
        )
        vega = math.exp((b - r) * t) * s * t__sqrt * norm.pdf(d1)
        rho = x * t * math.exp(-r * t) * norm.cdf(d2)
    elif option_type == OptionType.PUT:
        value = x * math.exp(-r * t) * norm.cdf(-d2) - (
            s * math.exp((b - r) * t) * norm.cdf(-d1)
        )
        delta = -math.exp((b - r) * t) * norm.cdf(-d1)
        gamma = math.exp((b - r) * t) * norm.pdf(d1) / (s * v * t__sqrt)
        theta = (
            -(s * v * math.exp((b - r) * t) * norm.pdf(d1)) / (2 * t__sqrt)
            + (b - r) * s * math.exp((b - r) * t) * norm.cdf(-d1)
            + r * x * math.exp(-r * t) * norm.cdf(-d2)
        )
        vega = math.exp((b - r) * t) * s * t__sqrt * norm.pdf(d1)
        rho = -x * t * math.exp(-r * t) * norm.cdf(-d2)

    return BSResult(value, delta, gamma, theta, vega, rho)
