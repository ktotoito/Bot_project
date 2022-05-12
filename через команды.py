from requests import request
import json
from telegram.ext import Updater, CallbackContext, CommandHandler
from telegram_config import TOKEN
import pymorphy2
from dictionaries import currency, crypto, periods

morph = pymorphy2.MorphAnalyzer(lang='ru')


def start(update, context):
    update.message.reply_text(
        f'''Привет, {update.message.chat.first_name}! 
* Чтобы узнать курс валюты, введи /course[валюта]
* Чтобы узнать курс криптовалюты, введи /cryptocourse[валюта]
* Чтобы узнать динамику криптовалюты за определённый отрезок времени, введи /dynamic[валюта][период]
Период может составлять минуту, 5, 15, 30, час, 4 часа, день, неделю, месяц или год.
По умолчанию периодом является 1 день''')


def course(update, context: CallbackContext):
    url = 'https://www.cbr-xml-daily.ru/daily_json.js'
    response = request('GET', url)
    n = json.loads(response.text)
    m = list(map(lambda x: x.lower(), context.args))
    k = set()
    for i in range(len(m)):
        if 'драм' not in m[i] and 'сша' not in m[i]:
            k.add(morph.parse(m[i])[0].normal_form)
        if 'драм' in m[i]:
            k.add('драм')
        if 'сша' in m[i]:
            k.add('сша')

    for i in list(currency.keys()):
        y = i.split()
        i1 = set(y)
        if k & i1 == i1:
            if ('сша' or 'фунт') not in y and len(y) > 1:
                r = morph.parse(y[1])[0].tag.gender
                if 'драм' in y:
                    r = 'masc'
                update.message.reply_text(
                    f'1 {morph.parse(y[0])[0].inflect({"ADJF", r, "sing"})[0]} {y[1]} = {n["Valute"][currency[i]]["Value"]}₽')
            else:
                update.message.reply_text(
                    f'1 {i} = {n["Valute"][currency[i]]["Value"]}₽')


def cryptocourse(update, context: CallbackContext):
    m = list(map(lambda x: x.lower(), context.args))
    k = set()
    for i in range(len(m)):
        if 'лайткоин' not in m[i] or 'лайткойн' not in m[i] or 'рипл' not in m[i] \
                or 'биткойн' not in m[i] or 'биткоин' not in m[i]:
            k.add(morph.parse(m[i])[0].normal_form)
        if 'лайткоин' in m[i]:
            k.add('лайткоин')
        if 'рипл' in m[i]:
            k.add('рипл')
        if 'биткойн' in m[i] or 'биткоин' in m[i]:
            k.add('биткойн')

    for i in list(crypto.keys()):
        y = i.split()
        i1 = set(y)
        if k & i1 == i1:
            url = f'https://api.huobi.pro/market/trade?symbol={crypto[i]}usdt'
            response = request('GET', url)
            bitcoin = json.loads(response.text)

            update.message.reply_text(f'1 {" ".join(y)} = {bitcoin["tick"]["data"][0]["price"]}$')


def help(update, context):
    update.message.reply_text(
        "Если у вас возникли вопросы, обратитесь к @Ktotoito")


def dynamic(update, context: CallbackContext):
    period = '1day'
    period_human = 'последний день'
    m = list(map(lambda x: x.lower(), context.args))

    for t in list(periods.keys()):
        t1 = set(t.split())
        if set(m) & t1 == t1:
            period = periods[t]
            period_human = t

    k = set()
    for i in range(len(m)):
        if 'лайткоин' not in m[i] or 'лайткойн' not in m[i] or 'рипл' not in m[i] \
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


def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("course", course))
    dp.add_handler(CommandHandler("cryptocourse", cryptocourse))
    dp.add_handler(CommandHandler("dynamic", dynamic))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
