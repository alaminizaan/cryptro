import ccxt
import time
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import asyncio
import aiohttp 

async def fetch_price(symbol):
    try:
        exchange = ccxt.binance()
        ticker = await exchange.fetch_ticker(symbol)
        return ticker['last']
    except Exception as e:
        print(f"Error fetching price for {symbol}: {e}")
        return None

async def main(symbols):
    with ThreadPoolExecutor(max_workers=10) as executor:
        loop = asyncio.get_event_loop()
        tasks = [loop.run_in_executor(executor, fetch_price, symbol) for symbol in symbols]
        prices = await asyncio.gather(*tasks)
    return prices

if __name__ == '__main__':
    symbols = ['BTC/USDT', 'ETH/USDT', 'XRP/USDT', 'LTC/USDT', 'BCH/USDT']
    prices = asyncio.run(main(symbols))
    avg_price = np.mean([price for price in prices if price is not None])
    print(f"Average price: {avg_price}")
