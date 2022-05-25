from requests import request
import json
from telegram.ext import Updater, CallbackContext, CommandHandler, MessageHandler, Filters
from telegram_config import TOKEN
import pymorphy2
from dictionaries import currency, crypto, periods

morph = pymorphy2.MorphAnalyzer(lang='ru')


def start(update, context):
    update.message.reply_text(
        f'''Привет, {update.message.chat.first_name}! 
* Чтобы узнать курс валюты, введи /course валюта
* Чтобы узнать курс криптовалюты, введи /crypto_course валюта
* Чтобы узнать динамику криптовалюты за определённый отрезок времени, введи /dynamic валюта период
Период может составлять минуту, 5, 15, 30, час, 4 часа, день, неделю, месяц или год.
По умолчанию периодом является 1 день
/last_ten вернёт последние 10 запрошенных курсов''')
    if 'last_ten1' in context.user_data:
        context.user_data['last_ten1'] = []
    # также можно сделать раздельно, типа 5 обычных валют и 5 крипто + динамика
    print(update.message.chat.first_name)
    print(update.message.chat.username)


def course(update, context: CallbackContext):
    if 'last_ten1' in context.user_data:
        context.user_data['last_ten1'] = []
    if context.args:
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
                print(i1)
                if i in context.user_data['last_ten1']:
                    context.user_data['last_ten1'].remove(i)
                    context.user_data['last_ten1'].append(i)
                else:
                    context.user_data['last_ten1'].append(i)
                if ('сша' or 'фунт') not in y and len(y) > 1:
                    r = morph.parse(y[1])[0].tag.gender
                    if 'драм' in y:
                        r = 'masc'
                    update.message.reply_text(
                        f'1 {morph.parse(y[0])[0].inflect({"ADJF", r, "sing"})[0]} {y[1]} = {n["Valute"][currency[i]]["Value"]}₽')
                else:
                    update.message.reply_text(
                        f'1 {i} = {n["Valute"][currency[i]]["Value"]}₽')
    print(update.message.chat.first_name)
    print(update.message.chat.username)


def crypto_course(update, context: CallbackContext):
    if 'last_ten1' in context.user_data:
        context.user_data['last_ten1'] = []
    if context.args:
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
                print(i1)
                if i in context.user_data['last_ten1']:
                    context.user_data['last_ten1'].remove(i)
                    context.user_data['last_ten1'].append(i)
                else:
                    context.user_data['last_ten1'].append(i)
                url = f'https://api.huobi.pro/market/trade?symbol={crypto[i]}usdt'
                response = request('GET', url)
                bitcoin = json.loads(response.text)

                update.message.reply_text(f'1 {" ".join(y)} = {bitcoin["tick"]["data"][0]["price"]}$')
    print(update.message.chat.first_name)
    print(update.message.chat.username)


def help(update, context):
    if 'last_ten1' in context.user_data:
        context.user_data['last_ten1'] = []
    update.message.reply_text(
        "Если у вас возникли вопросы, обратитесь к @Ktotoito")
    print(update.message.chat.first_name)
    print(update.message.chat.username)


def dynamic(update, context: CallbackContext):
    if 'last_ten1' in context.user_data:
        context.user_data['last_ten1'] = []
    period = '1day'
    period_human = 'день'
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
            print(i1)
            url = f'https://api.huobi.pro/market/history/kline?period={period}&size=1&symbol={crypto[i]}usdt'
            response = request('GET', url)
            e = json.loads(response.text)
            y = e["data"][0]["close"] / e["data"][0]["open"]
            if y > 1:
                update.message.reply_text(f'рост на {round(y * 100 - 100, 4)}% за {period_human}')
            elif y < 1:
                update.message.reply_text(f'снижение на {round(100 - y * 100, 4)}% за {period_human}')
    print(update.message.chat.first_name)
    print(update.message.chat.username)


def last_10(update, context: CallbackContext):
    if 'last_ten1' in context.user_data:
        context.user_data['last_ten1'] = []
    if context.user_data['last_ten1']:
        url = 'https://www.cbr-xml-daily.ru/daily_json.js'
        response = request('GET', url)
        n = json.loads(response.text)
        t = list(crypto.keys())
        currencies = []
        if len(context.user_data['last_ten1']) > 10:
            del context.user_data['last_ten1'][:-10]
        for i in context.user_data['last_ten1'][::-1]:
            if i in t:
                url = f'https://api.huobi.pro/market/trade?symbol={crypto[i]}usdt'
                response = request('GET', url)
                bitcoin = json.loads(response.text)
                currencies.append(f'1 {i} = {bitcoin["tick"]["data"][0]["price"]}$')
            else:
                i1 = i.split()
                if ('сша' or 'фунт') not in i1 and len(i1) > 1:
                    r = morph.parse(i1[1])[0].tag.gender
                    if 'драм' in i1:
                        r = 'masc'
                    currencies.append(
                        f'1 {morph.parse(i1[0])[0].inflect({"ADJF", r, "sing"})[0]} {i1[1]} = {n["Valute"][currency[i]]["Value"]}₽')
                else:
                    currencies.append(
                        f'1 {i} = {n["Valute"][currency[i]]["Value"]}₽')
        update.message.reply_text('\n'.join(currencies))

    else:
        update.message.reply_text('Вы пока не запрашивали никаких курсов')
    print(update.message.chat.first_name)
    print(update.message.chat.username)


def lol(update, context):
    if '(͡° ͜ʖ ͡°)' in update.message.text:
        update.message.reply_text('(͡° ͜ʖ ͡°)')
        print(update.message.chat.first_name)
        print(update.message.chat.username)


def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("course", course))
    dp.add_handler(CommandHandler("crypto_course", crypto_course))
    dp.add_handler(CommandHandler("dynamic", dynamic))
    dp.add_handler(CommandHandler("last_ten", last_10))
    dp.add_handler(MessageHandler(Filters.text, lol))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
