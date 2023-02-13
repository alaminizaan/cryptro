import ccxt
import time
import numpy as np
from concurrent.futures import ThreadPoolExecutor

def fetch_price(exchange, symbol):
    try:
        # Initialize the exchange object
        exchange = getattr(ccxt, exchange)()

        # Load the order book for the specified symbol
        order_book = exchange.fetch_order_book(symbol, limit=1)

        # Return the ask price (the lowest sell order)
        return float(order_book['asks'][0][0])
    except Exception as e:
        # Return a NaN value if an error occurs
        return np.nan

def find_arbitrage_opportunities():
    # Initialize the list of exchanges
    exchanges = ccxt.exchanges

    # Filter the exchanges to only those that support the EOS/USDT symbol
    exchanges = [exchange for exchange in exchanges if 'EOS/USDT' in eval(f"ccxt.{exchange}().load_markets()").keys()]

    # Create a dictionary to store the prices for each exchange
    prices = {}

    # Use a ThreadPoolExecutor to fetch the prices concurrently
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(fetch_price, exchange, 'EOS/USDT') for exchange in exchanges]

        for future in futures:
            exchange = exchanges[futures.index(future)]
            price = future.result()
            prices[exchange] = price

    # Iterate over the prices to find arbitrage opportunities
    for exchange, price in prices.items():
        if np.isnan(price):
            continue

        # Calculate the profit from buying on the current exchange and selling on all other exchanges
        for other_exchange, other_price in prices.items():
            if np.isnan(other_price) or exchange == other_exchange:
                continue

            profit = other_price - price

            # If the profit is positive, print the arbitrage opportunity
            if profit > 0:
                print(f"Arbitrage opportunity: buy on {exchange} at {price} and sell on {other_exchange} at {other_price} for a profit of {profit}")

if __name__ == '__main__':
    while True:
        find_arbitrage_opportunities()
        time.sleep(60)
