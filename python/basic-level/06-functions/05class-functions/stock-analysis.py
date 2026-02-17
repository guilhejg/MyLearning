stock_prices = [
    34.68, 36.09, 34.94, 33.97, 34.68,
    35.82, 43.41, 44.29, 44.65, 53.56,
    49.85, 48.71, 48.71, 49.94, 48.53,
    47.03, 46.59, 48.62, 44.21, 47.21
]


def price_at(x):
    # x is the day (1–20), list index is (0–19)
    return stock_prices[x - 1]


def max_price(a, b):
    # get prices from day a to day b
    return max(stock_prices[a - 1:b])


def min_price(a, b):
    # get prices from day a to day b
    return min(stock_prices[a - 1:b])


# ---- calling the functions (testing) ----

print(price_at(1))      # price on day 1
print(max_price(1, 5))  # max price from day 1 to day 5
print(min_price(10, 15)) # min price from day 10 to day 15