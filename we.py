from requests import request
import json
from telegram.ext import Updater, MessageHandler, Filters, ConversationHandler
from telegram.ext import CallbackContext, CommandHandler
from telegram_config import TOKEN
import pymorphy2
from dictionaries import currency, crypto, periods

morph = pymorphy2.MorphAnalyzer(lang='ru')


def start(update, context):
    update.message.reply_text(
        f'''Привет, {update.message.from_user.username}!''')
    return 1


def help(update, context):
    update.message.reply_text(
        "Если у вас возникли вопросы, обратитесь к @Ktotoito")


def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("help", help))
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            1: [MessageHandler(Filters.text, currency_exchange)]
        },
        fallbacks=[]
    )
    dp.add_handler(conv_handler)

    # text_handler1 = MessageHandler(Filters.text, exchange_rate1)
    # text_handler = MessageHandler(Filters.text, exchange_rate)
    # text_handler1 = MessageHandler(Filters.text, currency)
    # dp.add_handler(text_handler)
    # dp.add_handler(text_handler)
    # dp.add_handler(text_handler1)
    updater.start_polling()

    updater.idle()


# def exchange_rate1(update, context):
#     a = update.message.text.lower()
#     if 'курс' in a and ('биткоин' in a or 'битк' in a):
#         url = 'https://api.huobi.pro/market/trade?symbol=btcusdt'
#         response = request('GET', url)
#         r = json.loads(response.text)
#         update.message.reply_text(f'Биток: {r["tick"]["data"][0]["price"]}$')
#
#     if 'курс' in a and (' эфириум' in a or ' эфирчик' in a or ' эфир' in a):
#         url = 'https://api.huobi.pro/market/trade?symbol=ethusdt'
#         response = request('GET', url)
#         r = json.loads(response.text)
#         update.message.reply_text(f'Эфирчик: {r["tick"]["data"][0]["price"]}$')


# def exchange_rate(update, context):
#     if 'курс' in update.message.text and ('крипт' in update.message.text):
#         url = 'https://api.huobi.pro/market/trade?symbol=btcusdt'
#         response = request('GET', url)
#         bitcoin = json.loads(response.text)
#
#         url1 = 'https://api.huobi.pro/market/trade?symbol=ethusdt'
#         response = request('GET', url1)
#         ethereum = json.loads(response.text)
#         # url2 = 'https://api.huobi.pro/market/detail?symbol=ethusdt'
#         # response = request('GET', url2)
#         # ethereum1 = json.loads(response.text)
#         # f1 = round(ethereum["tick"]["data"][0]["price"] / ethereum1["tick"]["open"] * 100, 2)
#         # g = ''
#         # if f1 > 100:
#         #     g = 'рост на'
#         # elif f1 < 100:
#         #     g = 'снижение на'
#         # f = abs(f1 - 100)
#
#         update.message.reply_text(f'Курс Биткоина: {bitcoin["tick"]["data"][0]["price"]}$\n'
#                                   f'Курс Эфириума: {ethereum["tick"]["data"][0]["price"]}$')
#     else:
#         pass


def currency_exchange(update, context):
    if 'курс' in update.message.text:

        m = update.message.text.lower().split()
        k = set()
        for i in range(len(m)):
            if 'драм' not in m[i] or 'лайткоин' not in m[i] or 'рипл' not in m[i]\
                    or 'биткойн' not in m[i] or 'биткоин' not in m[i]:
                k.add(morph.parse(m[i])[0].normal_form)
            if 'драм' in m[i]:
                k.add('драм')
            if 'лайткоин' in m[i]:
                k.add('лайткоин')
            if 'рипл' in m[i]:
                k.add('рипл')
            if 'биткойн' in m[i] or 'биткоин' in m[i]:
                k.add('биткойн')

        if not set(crypto.keys()) & k or not ('bitcoin' and 'cash') in k or not ('биткойн' and 'кэш') in k:

            url = 'https://www.cbr-xml-daily.ru/daily_json.js'
            response = request('GET', url)
            n = json.loads(response.text)

            for i in list(currency.keys()):
                i1 = set(i.split())
                if k & i1 == i1 and 'фунт' not in k:
                    update.message.reply_text(f'Курс: {n["Valute"][currency[i]]["Value"]}')
                if 'фунт' in k:
                    update.message.reply_text(f'Курс: {n["Valute"][currency[i]]["Value"]}')

        if set(crypto.keys()) & k or ('bitcoin' and 'cash') in k or ('биткойн' and 'кэш') in k:
            print('yes')
            for i in list(crypto.keys()):
                i1 = set(i.split())
                if k & i1 == i1:
                    url = f'https://api.huobi.pro/market/trade?symbol={crypto[i]}usdt'
                    response = request('GET', url)
                    bitcoin = json.loads(response.text)

                    update.message.reply_text(f'Курс: {bitcoin["tick"]["data"][0]["price"]}$')

            # url1 = 'https://api.huobi.pro/market/trade?symbol=ethusdt'
            # response = request('GET', url1)
            # ethereum = json.loads(response.text)
            # # url2 = 'https://api.huobi.pro/market/detail?symbol=ethusdt'
            # # response = request('GET', url2)
            # # ethereum1 = json.loads(response.text)
            # # f1 = round(ethereum["tick"]["data"][0]["price"] / ethereum1["tick"]["open"] * 100, 2)
            # # g = ''
            # # if f1 > 100:
            # #     g = 'рост на'
            # # elif f1 < 100:
            # #     g = 'снижение на'
            # # f = abs(f1 - 100)
            #
            # update.message.reply_text(f'Курс Биткоина: {bitcoin["tick"]["data"][0]["price"]}$\n'
            #                           f'Курс Эфириума: {ethereum["tick"]["data"][0]["price"]}$')

    if 'статистик' in update.message.text or 'динамик' in update.message.text:
        period = '1day'
        period_human = 'последний день'
        m = update.message.text.lower().split()

        for t in list(periods.keys()):
            t1 = set(t.split())
            if set(m) & t1 == t1:
                period = periods[t]
                period_human = t

        k = set()
        for i in range(len(m)):
            if 'лайткоин' not in m[i] or 'рипл' not in m[i]\
                    or 'биткойн' not in m[i] or 'биткоин' not in m[i]:
                k.add(morph.parse(m[i])[0].normal_form)
            if 'лайткоин' in m[i]:
                k.add('лайткоин')
            if 'рипл' in m[i]:
                k.add('рипл')
            if 'биткойн' in m[i] or 'биткоин' in m[i]:
                k.add('биткойн')

        for i in list(crypto.keys()):
            i1 = set(i.split())
            if k & i1 == i1:
                url = f'https://api.huobi.pro/market/history/kline?period={period}&size=1&symbol={crypto[i]}usdt'
                response = request('GET', url)
                e = json.loads(response.text)
                y = e["data"][0]["close"] / e["data"][0]["open"]
                if y > 1:
                    update.message.reply_text(f'рост на {round(y * 100 - 100, 4)}% за {period_human}')
                elif y < 1:
                    update.message.reply_text(f'снижение на {round(100 - y * 100, 4)}% за {period_human}')


if __name__ == '__main__':
    main()

# url = 'https://api.huobi.pro/market/trade?symbol=ethusdt'
# response = request('GET', url)
# r = json.loads(response.text)
# url1 = 'https://api.huobi.pro/market/trade?symbol=btcusdt'
# response1 = request('GET', url1)
# m = json.loads(response1.text)
# print("Эфирчик:", r["tick"]['data'][0]['price'])
# print("Биток:", m["tick"]['data'][0]['price'])