import ccxt
import time
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import asyncio
import aiohttp 

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.json()

async def get_prices(symbol):
    try:
        async with aiohttp.ClientSession() as session:
            exchange = ccxt.binance()
            exchange.load_markets()
            symbol = exchange.symbols[0]
            price = await fetch(session, exchange.urls['api']['ticker'] % (symbol))
            return price['last']
    except Exception as e:
        print(f'Error: {e}')
        return np.nan

async def main():
    symbols = ['BTC/USDT', 'ETH/USDT', 'XRP/USDT', 'LTC/USDT']
    with ThreadPoolExecutor(max_workers=10) as executor:
        loop = asyncio.get_event_loop()
        futures = [
            loop.run_in_executor(
                executor,
                get_prices,
                symbol
            )
            for symbol in symbols
        ]
        for response in await asyncio.gather(*futures):
            print(response)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
