import logging
from datetime import datetime

from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from app.config import API_KEY, PROXY
from app import rzd
from app.model import Subscribes

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename='bot.log'
                    )
CHATS_TRAINS = {}


def get_train_button(train):
    return '(%s) %s %s' % (
        train.number, train.departure_time.strftime("%H:%M %d.%m"), train.arrival_time.strftime("%H:%M %d.%m"))


def get_train_info(train):
    result = '(%s) %s \nОтправление: %s\nПрибытие: %s\n\n' % (
        train.number, train.title, train.departure_time.strftime("%H:%M %d.%m.%Y"),
        train.arrival_time.strftime("%H:%M %d.%m.%Y"))
    return result + '\n'.join([str(seat) for seat in dict(train.seats).values()])


def get_train(route_from, route_to, route_date):
    with rzd.RzdFetcher() as fetcher:
        train_list = fetcher.trains(
            route_from.upper(),
            route_to.upper(),
            rzd.TimeRange(
                datetime(route_date.year, route_date.month,
                         route_date.day,
                         0, 0),
                datetime(route_date.year, route_date.month,
                         route_date.day, 23, 59),
            )
        )
    return train_list


def build_menu(buttons,
               n_cols,
               header_buttons=None,
               footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu


def get_route(bot, update):
    text = update.message.text.split()
    logging.info(text)
    if len(text) == 1:
        update.message.reply_text('Введите значение после команды')
    rout_from = text[1]
    route_to = text[2]
    route_date = datetime.strptime(text[3], "%d-%m-%y")
    trains = get_train(rout_from, route_to, route_date)
    CHATS_TRAINS[update.message.chat.id] = {train.number: train for train in trains}
    button_list = [InlineKeyboardButton(get_train_button(train), callback_data=train.number)
                   for train in trains
                   ]
    reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=1))
    bot.send_message(update.message.chat.id, "Список поездов", reply_markup=reply_markup)
    # except Exception as e:
    #     logging.info(e)
    #     update.message.reply_text('не правильно введена команда')


def get_route2(bot, update):
    text = update.message.text.split()
    logging.info(text)
    try:
        if len(text) == 1:
            update.message.reply_text('Введите значение после команды')
        rout_from = text[1]
        route_to = text[2]
        route_date = datetime.strptime(text[3], "%d-%m-%y")
        trains = get_train(rout_from, route_to, route_date)
        CHATS_TRAINS[update.message.chat.id] = {train.number: train for train in trains}
        message = '\n'.join([str(train) for train in trains])
        button_list = [InlineKeyboardButton(train.number, callback_data=train.number)
                       for train in trains
                       ]
        reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=1))
        bot.send_message(update.message.chat.id, "Список поездов: \n{}".format(message), reply_markup=reply_markup)
    except Exception as e:
        logging.info(e)
        update.message.reply_text(
            'не правильно введена команда\nвведите команду в формате\nотправление прибытие дата\nдата в формате дд-мм-гг')


def callbackHandler(bot, call):
    logging.info(call)
    logging.info(CHATS_TRAINS)
    if call.callback_query:
        if call.callback_query.data:
            if CHATS_TRAINS[call.callback_query.message.chat.id] and call.callback_query.data in CHATS_TRAINS[
                call.callback_query.message.chat.id].keys():
                bot.send_message(chat_id=call.callback_query.message.chat.id, text=get_train_info(
                    CHATS_TRAINS[call.callback_query.message.chat.id][call.callback_query.data]))

            # bot.edit_message_text(chat_id=call.callback_query.message.chat.id,
            #                       message_id=call.callback_query.message.message_id, text=call.callback_query.data)


def subscribe(bot, update):
    text = update.message.text.split()
    logging.info(text)
    if len(text) == 1:
        update.message.reply_text('Введите значение после команды')
    route_from = text[1]
    route_to = text[2]
    route_date = datetime.strptime(text[3], "%d-%m-%y")
    _subscribe = Subscribes(chat_id=update.message.chat.id, route_from=route_from, route_to=route_to, route_date=route_date)


def main():
    mybot = Updater(API_KEY, request_kwargs=PROXY)

    logging.info('Бот запускается')
    dp = mybot.dispatcher
    dp.add_handler(CommandHandler('route', get_route))
    dp.add_handler(CommandHandler('subscribe', subscribe))
    dp.add_handler(CallbackQueryHandler(callbackHandler))

    mybot.start_polling()
    mybot.idle()


if __name__ == '__main__':
    main()
