import ccxt
import time
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import asyncio
import aiohttp

# Initialize the Binance and Kucoin exchanges
binance = ccxt.binance({
    'apiKey': 'BINANCE_API_KEY',
    'secret': 'BINANCE_SECRET_KEY',
})
kucoin = ccxt.kucoin({
    'apiKey': 'KUCOIN_API_KEY',
    'secret': 'KUCOIN_SECRET_KEY',
})

# Set the base currency to USDT
base_currency = 'USDT'

async def fetch_price(exchange, symbol):
    async with aiohttp.ClientSession() as session:
        async with session.get(exchange.urls['api']['ticker'].format(symbol=symbol)) as response:
            price_data = await response.json()
            return float(price_data['last'])

async def fetch_fees(exchange, symbol):
    trading_fee = await exchange.fetch_trading_fee(symbol)
    transaction_fee = await exchange.fetch_transaction_fee(symbol)
    return trading_fee, transaction_fee

async def trade_arbitrage():
    try:
        # Get the current price of EOS/USDT on both exchanges asynchronously
        binance_price = await fetch_price(binance, 'EOS/USDT')
        kucoin_price = await fetch_price(kucoin, 'EOS/USDT')

        # Get the trading fees for both exchanges asynchronously
        binance_trading_fee, binance_transaction_fee = await fetch_fees(binance, 'EOS/USDT')
        kucoin_trading_fee, kucoin_transaction_fee = await fetch_fees(kucoin, 'EOS/USDT')

        # Calculate the spread between the two exchanges
        spread = kucoin_price * (1 + kucoin_transaction_fee + kucoin_trading_fee) - binance_price * (1 - binance_trading_fee)

        # Check if there is an arbitrage opportunity for a buy trade
        if spread > 0:
            # Get the market depth for both exchanges asynchronously
            binance_depth = await binance.fetch_order_book('EOS/USDT')
            kucoin_depth = await kucoin.fetch_order_book('EOS/USDT')

            # Calculate the optimal order size to minimize slippage
            binance_order_size = np.minimum(binance_depth['asks'][0][1], kucoin_depth['bids'][0][1])
            kucoin_order_size = binance_order_size

            # Convert USDT to the base currency on Binance
           await binance.create_order(symbol=f'{base_currency}/USDT', type='limit', side='sell', amount=binance_order_size, price=binance_price)

        # Buy EOS with the base currency on Kucoin
        await kucoin.create_order(symbol='EOS/USDT', type='limit', side='buy', amount=kucoin_order_size, price=kucoin_price)

        # Convert EOS to USDT on Binance
        await binance.create_order(symbol='EOS/USDT', type='limit', side='sell', amount=kucoin_order_size, price=binance_price)

        # Sell USDT for the base currency on Kucoin
        await kucoin.create_order(symbol=f'{base_currency}/USDT', type='limit', side='buy', amount=kucoin_order_size, price=kucoin_price)

    # Check if there is an arbitrage opportunity for a sell trade
    elif spread < 0:
        # Get the market depth for both exchanges asynchronously
        binance_depth = await binance.fetch_order_book('EOS/USDT')
        kucoin_depth = await kucoin.fetch_order_book('EOS/USDT')

        # Calculate the optimal order size to minimize slippage
        binance_order_size = np.minimum(binance_depth['bids'][0][1], kucoin_depth['asks'][0][1])
        kucoin_order_size = binance_order_size

        # Buy EOS with USDT on Binance
        await binance.create_order(symbol='EOS/USDT', type='limit', side='buy', amount=binance_order_size, price=binance_price)

        # Sell EOS for USDT on Kucoin
        await kucoin.create_order(symbol='EOS/USDT', type='limit', side='sell', amount=kucoin_order_size, price=kucoin_price)

        # Convert EOS to the base currency on Binance
        await binance.create_order(symbol=f'EOS/{base_currency}', type='limit', side='sell', amount=binance_order_size, price=binance_price)

        # Buy USDT with the base currency on Kucoin
        await kucoin.create_order(symbol=f'USDT/{base_currency}', type='limit', side='buy', amount=kucoin_order_size, price=kucoin_price)
