from requests import request
import json
from telegram.ext import Updater, MessageHandler, Filters, ConversationHandler
from telegram.ext import CallbackContext, CommandHandler
# from telegram_config import TOKEN
import pymorphy2
from dictionaries import currency, crypto, periods

morph = pymorphy2.MorphAnalyzer(lang='ru')
TOKEN = '5284374471:AAExiDe1N_LSX7SFc-rvD8PnTFIObVToLX0'


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

    updater.start_polling()

    updater.idle()


def currency_exchange(update, context):
    if 'курс' in update.message.text.lower():

        m = update.message.text.lower().split()
        k = set()
        for i in range(len(m)):
            if 'драм' not in m[i] or 'лайткоин' not in m[i] or 'рипл' not in m[i] \
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
                if k & i1 == i1:
                    update.message.reply_text(f'Курс: {n["Valute"][currency[i]]["Value"]}')

        if set(crypto.keys()) & k or ('bitcoin' and 'cash') in k or ('биткойн' and 'кэш') in k:
            for i in list(crypto.keys()):
                i1 = set(i.split())
                if k & i1 == i1:
                    url = f'https://api.huobi.pro/market/trade?symbol={crypto[i]}usdt'
                    response = request('GET', url)
                    bitcoin = json.loads(response.text)

                    update.message.reply_text(f'Курс: {bitcoin["tick"]["data"][0]["price"]}$')

    if 'статистик' in update.message.text.lower() or 'динамик' in update.message.text.lower():
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
            if 'лайткоин' not in m[i] or 'рипл' not in m[i] \
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

