import ccxt
import time
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import asyncio
import aiohttp

async def get_price(symbol, exchange):
    try:
        exchange = getattr(ccxt, exchange)()
        ticker = await exchange.fetch_ticker(symbol)
        return ticker['last']
    except Exception as e:
        print(f'An error occurred: {e}')
        return None

async def main(symbols, exchanges):
    tasks = []
    for symbol in symbols:
        for exchange in exchanges:
            task = asyncio.ensure_future(get_price(symbol, exchange))
            tasks.append(task)
    responses = await asyncio.gather(*tasks)
    return responses

if __name__ == '__main__':
    symbols = ['BTC/USD', 'ETH/USD', 'LTC/USD']
    exchanges = ['binance', 'kraken']

    loop = asyncio.get_event_loop()
    prices = loop.run_until_complete(main(symbols, exchanges))

    for i, symbol in enumerate(symbols):
        for j, exchange in enumerate(exchanges):
            index = i * len(exchanges) + j
            price = prices[index]
            if price is not None:
                print(f'{symbol} on {exchange} is trading at {price}')
            else:
                print(f'Error retrieving price for {symbol} on {exchange}')
    loop.close()
