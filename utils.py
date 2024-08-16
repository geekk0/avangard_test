import httpx

from bot_setup import logger, redis_conn, bot


async def get_crypto_price(crypto):
    logger.info(f"Getting crypto price for {crypto}")
    url = 'https://pro-api.coinmarketcap.com/v1/tools/price-conversion'
    parameters = {
        'amount': '1',
        'symbol': crypto,
        'convert': 'USD'
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': 'd89b8662-1629-4aaf-8756-c3d32bad6a05',
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=parameters, headers=headers)
        data = response.json()

        logger.info(f"Got crypto response: {data}")

        logger.info(f"Got crypto price: {data['data']['quote']['USD']['price']} USD")

        coin_price_usd = data['data']['quote']['USD']['price']

        return coin_price_usd


async def check_prices():
    logger.info("Checking prices")
    keys = await redis_conn.keys("crypto:*")
    for key in keys:
        parts = key.decode().split(":")
        chat_id = parts[1]
        crypto = parts[2]
        limits = await redis_conn.hgetall(key)
        min_price = float(limits[b'min_price'])
        max_price = float(limits[b'max_price'])
        price = await get_crypto_price(crypto)
        last_price_key = f"last_price:{chat_id}:{crypto}"
        last_price = await redis_conn.get(last_price_key)
        if last_price is None or float(last_price) != price:
            if price < min_price or price > max_price:
                await bot.send_message(chat_id, f'Курс {crypto} достиг порогового значения: {round(price, 2)} USD')
                logger.info(f'Курс {crypto} достиг порогового значения: {round(price, 2)} USD')
            await redis_conn.set(last_price_key, price)
