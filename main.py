import sys
import aiohttp
import asyncio
import platform
from datetime import datetime, timedelta


CURRENCIES = [
    'AUD', 'CAD', 'CZK', 'DKK', 'HUF', 'ILS', 'JPY', 'LVL', 'LTL', 'NOK', 'SKK', 'SEK', 'CHF', 'GBP', 'BYR', 'GEL', 'PLZ'
]


class HttpError(Exception):
    pass


async def request(url: str):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    return result
                else:                                                 # обробка помилки 404
                    raise HttpError(f"Error status: {resp.status} for {url}")
        except (aiohttp.ClientConnectorError, aiohttp.InvalidURL) as err:  # обробка інших помилок
            raise HttpError(f'Connection error: {url}', str(err))


async def choise(data: dict, currency: str):
    await asyncio.sleep(0)
    dict = list(filter(lambda x: x.get('currency') == currency, data['exchangeRate']))[0]
    return {currency: {'sale': dict.get('saleRateNB'), 'purchase': dict.get('purchaseRateNB')}}


async def data_adapter(data: dict, currencies: tuple) -> dict:
    result = {}
    for curr in currencies:
        result.update(await choise(data, curr))
    # eur_dict = await choise(data, 'EUR')
    # usd_dict = await choise(data, 'USD')
    # {data['date']: {'EUR': eur_dict, 'USD': usd_dict}}
    return {data['date']: result}


async def main(*args):
    if 1 > int(args[1]) > 10:
        return "Кількість днів повинна бути від 1 до 10"
    arguments_currency = ["EUR", "USD"]
    if len(args) > 2:
        for el in args[1:]:
            if el.upper() in CURRENCIES:
                arguments_currency.append(el.upper())
    result = []
    today = datetime.now()
    current_day = today - timedelta(days=int(args[1]))
    try:
        while current_day != today:
            shift = current_day.strftime("%d.%m.%Y")
            respons = await request(f'https://api.privatbank.ua/p24api/exchange_rates?date={shift}')
            result.append(await data_adapter(respons, tuple(arguments_currency)))
            current_day = current_day + timedelta(days=1)
        return result
        # respons = await request('https://api.privatbank.ua/p24api/pubinfo?exchange&coursid=5')
        # return respons
    except HttpError as err:
        print(err)


if __name__ == '__main__':
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    print(sys.argv)
    r = asyncio.run(main(*sys.argv))
    print(r)
