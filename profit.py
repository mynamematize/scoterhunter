def estimate_profit(buy_price: float, resale_price: float, repair_cost: float = 0, delivery_cost: float = 0, risk_reserve: float = 0):
    """Simple net estimate; not a guarantee of actual resale value."""
    costs = buy_price + repair_cost + delivery_cost + risk_reserve
    return {
        "costs": costs,
        "gross": resale_price - buy_price,
        "net": resale_price - costs,
    }
