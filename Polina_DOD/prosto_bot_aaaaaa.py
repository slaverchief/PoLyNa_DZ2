import logging

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup,\
    KeyboardButton, PollAnswer, Poll, ReplyKeyboardRemove

from datetime import datetime, timedelta

import asyncio
import sqlite3
import json

#подключение к базе данных
conn = sqlite3.connect('my.db')
cursor = conn.cursor()

TOKEN = '6731829772:AAF-fGyjjw2MNcr2xn4YlH7bLR6uGOp17rA'
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

async def on_startup(_):
    print('Бот вышел в онлайн')

#создание необхимых таблиц в базе данных
cursor.execute('''CREATE TABLE IF NOT EXISTS user_stat (
                    user_id INTEGER,
                    timestamp TEXT
                )''')
cursor.execute('''CREATE TABLE IF NOT EXISTS url (
                    user_id INTEGER,
                    timestampurl TEXT
                )''')
cursor.execute('''CREATE TABLE IF NOT EXISTS user_votes (
                    user_id INTEGER,
                    answer TEXT
                )''')

#вызов, после нажатия старт, клавиатуры (кнопки - новый маршрут, библиотека карт) и программы ДОДа
@dp.message_handler(commands=['start'])
async def commands_start(message: types.Message):
    user_id = message.from_user.id
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('INSERT INTO user_stat (user_id, timestamp) VALUES (?, ?)', (user_id, timestamp))
    conn.commit()

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

    button_new_marshrut = KeyboardButton('Новый маршрут 📌')
    keyboard.add(button_new_marshrut)

    url_button = types.KeyboardButton(text='Библиотека карт 🗺')
    keyboard.add(url_button)

    pdf_file = 'Программа Дня открытых дверей.pdf'

    try:
        with open(pdf_file, 'rb') as file:
            await bot.send_document(chat_id=message.chat.id, document=file)
    except FileNotFoundError:
        logging.error(f'Файл {pdf_file} не найден.')
        await message.answer('Файл не найден.')

    await message.answer('Чтобы продолжить, нажмите на кнопку «Новый маршрут», кнопка расположена внизу экрана.', reply_markup=keyboard)

#обновление бота
@dp.message_handler(commands=['restart'])
async def commands_start(message: types.Message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

    button_new_marshrut = KeyboardButton('Новый маршрут 📌')
    keyboard.add(button_new_marshrut)

    url_button = types.KeyboardButton(text='Библиотека карт 🗺')
    keyboard.add(url_button)

    await message.answer('Чтобы продолжить, нажми на кнопку «Новый маршрут», кнопка расположена внизу экрана.', reply_markup=keyboard)

#команда для отправления ссылки на сайт библиотеки карт
@dp.message_handler(lambda message: message.text == 'Библиотека карт 🗺')
async def open_website(message: types.Message):
    user_id = message.from_user.id
    timestampurl = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('INSERT INTO url (user_id, timestampurl) VALUES (?, ?)', (user_id, timestampurl))
    conn.commit()

    website_url = 'https://mospolynavigation.github.io/dod/'
    await message.answer(f'Перейти к просмотру → <a href="{website_url}">«Библиотека карт»</a>', disable_web_page_preview=True, parse_mode=types.ParseMode.HTML)


#функции для подсчета общего количества пользователей за определенный период времени (за весь период, декабрь, январь и тд)
async def count_users_stat(start_time, end_time):
    cursor.execute('SELECT COUNT(DISTINCT user_id) FROM user_stat WHERE timestamp BETWEEN ? AND ?', (start_time, end_time))
    total_users = cursor.fetchone()[0]
    return total_users

async def count_users_December(start_December, end_December):
    cursor.execute('SELECT COUNT(DISTINCT user_id) FROM user_stat WHERE timestamp BETWEEN ? AND ? AND user_id NOT IN (SELECT DISTINCT user_id FROM user_stat WHERE timestamp < ?)',
                   (start_December, end_December, start_December))
    users_December = cursor.fetchone()[0]
    return users_December

async def count_users_January(start_January, end_January):
    cursor.execute('SELECT COUNT(DISTINCT user_id) FROM user_stat WHERE timestamp BETWEEN ? AND ? AND user_id NOT IN (SELECT DISTINCT user_id FROM user_stat WHERE timestamp < ?)',
                   (start_January, end_January, start_January))
    users_January = cursor.fetchone()[0]
    return users_January

async def count_users_February(start_February, end_February):
    cursor.execute('SELECT COUNT(DISTINCT user_id) FROM user_stat WHERE timestamp BETWEEN ? AND ? AND user_id NOT IN (SELECT DISTINCT user_id FROM user_stat WHERE timestamp < ?)',
                   (start_February, end_February, start_February))
    users_February = cursor.fetchone()[0]
    return users_February



#команда для бота, чтобы увидеть общее количество новых пользователей за выбранный период времени
@dp.message_handler(commands=['users'])
async def get_users_stat(message: types.Message):
    start_time = '2023-01-01 00:00:00'  #начальное время
    end_time = '2024-12-31 23:59:59'  #конечное время
    total_users = await count_users_stat(start_time, end_time)

    end_December = '2023-12-31 23:59:59'
    start_December = '2023-12-01 00:00:00'
    users_December = await count_users_December(start_December, end_December)

    end_January = '2024-01-31 23:59:59'
    start_January = '2024-01-01 00:00:00'
    users_January = await count_users_January(start_January, end_January)

    end_February = '2024-02-29 23:59:59'
    start_February = '2024-02-01 00:00:00'
    users_February = await count_users_February(start_February, end_February)
    await message.answer(f'Общее количество пользователей за весь период времени: {total_users} \n\nза декабрь 2023: {users_December} \nза январь 2024: {users_January} \nза февраль 2024: {users_February}')


#функции для подсчета общего количества пользователей за выбранный период времени (за весь период, декабрь, январь и тд)
async def count_users_url(start_url, end_url):
    cursor.execute('SELECT COUNT(DISTINCT user_id) FROM url WHERE timestampurl BETWEEN ? AND ?', (start_url, end_url))
    total_url = cursor.fetchone()[0]
    return total_url

async def count_users_url_December(start_url_December, end_url_December):
    cursor.execute('SELECT COUNT(DISTINCT user_id) FROM url WHERE timestampurl BETWEEN ? AND ? AND user_id NOT IN (SELECT DISTINCT user_id FROM url WHERE timestampurl < ?)',
                   (start_url_December, end_url_December, start_url_December))
    users_url_December = cursor.fetchone()[0]
    return users_url_December



async def count_users_url_January(start_url_January, end_url_January):
    cursor.execute('SELECT COUNT(DISTINCT user_id) FROM url WHERE timestampurl BETWEEN ? AND ? AND user_id NOT IN (SELECT DISTINCT user_id FROM url WHERE timestampurl < ?)',
                   (start_url_January, end_url_January, start_url_January))
    users_url_January = cursor.fetchone()[0]
    return users_url_January

async def count_users_url_February(start_url_February, end_url_February):
    cursor.execute('SELECT COUNT(DISTINCT user_id) FROM url WHERE timestampurl BETWEEN ? AND ? AND user_id NOT IN (SELECT DISTINCT user_id FROM url WHERE timestampurl < ?)',
                   (start_url_February, end_url_February, start_url_February))
    users_url_February = cursor.fetchone()[0]
    return users_url_February

#команда для бота, чтобы увидеть общее количество пользователей за выбранный период времени (для библиотеки карт)
@dp.message_handler(commands=['url'])
async def get_users_url(message: types.Message):
    start_url = '2023-01-01 00:00:00'  #начальное время
    end_url = '2024-12-31 23:59:59'  #конечное время
    total_url = await count_users_url(start_url, end_url)

    end_url_December = '2023-12-31 23:59:59'
    start_url_December = '2023-12-01 00:00:00'
    users_url_December = await count_users_url_December(start_url_December, end_url_December)

    end_url_January = '2024-01-31 23:59:59'
    start_url_January = '2024-01-01 00:00:00'
    users_url_January = await count_users_url_January(start_url_January, end_url_January)

    end_url_February = '2024-02-29 23:59:59'
    start_url_February = '2024-02-01 00:00:00'
    users_url_February = await count_users_url_February(start_url_February, end_url_February)
    await message.answer(f'Общее количество пользователей за весь период времени, перешедших по ссылке: {total_url} \n\nза декабрь 2023: {users_url_December}  \nза январь 2024: {users_url_January} \nза февраль 2024: {users_url_February} ')



poll_results = {}  #переменная для хранения результатов опросов
#отправка опроса в определенный день и время
async def send_poll():
    #день, месяц, год и время отправки опроса
    scheduled_time = datetime(2024, 2, 10, 18, 0, 0)

    #ожидание до момента отправки опроса
    while datetime.now() < scheduled_time:
        await asyncio.sleep(60)  #проверка каждую минуту

    #получение списка пользователей, которые воспользовались командой старт в заданный период
    start_time = '2024-02-01 00:00:00'
    end_time = '2024-02-12 23:59:59'
    users = await get_users_in_period(start_time, end_time)

    #отправка опроса каждому пользователю из списка
    for user_id in users:
        poll_message = await bot.send_poll(chat_id=user_id,
                                           question='День открытых дверей окончен.\nОцените пожалуйста работу бота.',
                                           options=['1', '2', '3', '4', '5'])

        #запись результатов опроса
        await asyncio.sleep(14400)
        poll_result = await bot.stop_poll(chat_id=user_id, message_id=poll_message.message_id)
        poll_results[user_id] = poll_result


#получение результатов опроса
@dp.message_handler(commands=['results'])
async def results(message: types.Message):
    user_id = message.from_user.id
    if user_id in poll_results:
        total = poll_results[user_id].options
        await message.answer(f'Результаты опроса:\n {total} ')
    else:
        await message.answer('Результаты опроса еще не доступны')

# Функция для получения списка пользователей, воспользовавшихся командой старт в заданный период
async def get_users_in_period(start_time, end_time):
    cursor.execute('SELECT DISTINCT user_id FROM user_stat WHERE timestamp BETWEEN ? AND ?', (start_time, end_time))
    users = [row[0] for row in cursor.fetchall()]
    return users

async def scheduler():
    while True:
        try:
            await send_poll()
        except Exception as e:
            print(f'An error occurred: {e}')
        finally:
            await asyncio.sleep(86400)  #повтор проверки каждые 24 часа (86400 секунды)



#эта штучка нужна, если вдруг пользователь нажмёт в описании бота на данную команду (по факту делает то же самое, что и команда старт)
@dp.message_handler(commands=['newroute'])
async def commands_start(message: types.Message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    button_new_marshrut = KeyboardButton('Новый маршрут 📌')
    keyboard.add(button_new_marshrut)

    url_button = types.KeyboardButton(text='Библиотека карт 🗺')
    keyboard.add(url_button)

    await message.answer("Чтобы продолжить, нажми на кнопку «Новый маршрут», она находится внизу экрана:", reply_markup=keyboard)


#вывод сообщения после нажатия на кнопку новый маршрут
@dp.message_handler(lambda message: message.text == 'Новый маршрут 📌')
async def url_command(message : types.Message):
	await message.answer('Выбери, что хочешь посетить:  👀', reply_markup=urlkb)


#команда описания бота
@dp.message_handler(commands=['description'])
async def cmd_description(message: types.Message):
    description_file = f'descriptions_language_ru.txt'
    try:
        with open(description_file, 'r', encoding='utf-8') as file:
            description = file.read()
            await message.answer(description, parse_mode="HTML")
            await message.answer('🕊')
    except FileNotFoundError:
        logging.error(f'Файл {description_file} не найден.')
        await message.answer('Описание не найдено.')


#создание инлайн кнопок для выбора мероприятия ДОДа
urlkb = InlineKeyboardMarkup(row_width=1)
urlButton1 = InlineKeyboardButton(text='Официальная часть', callback_data='v1')
urlButton2 = InlineKeyboardButton(text='Мастер-классы', callback_data='v2')
urlButton3 = InlineKeyboardButton(text='Приёмная комиссия', callback_data='v3')
urlButton4 = InlineKeyboardButton(text='Выставка проектов', callback_data='v4')
urlButton5 = InlineKeyboardButton(text='Выставочная зона', callback_data='v5')
urlButton6 = InlineKeyboardButton(text='Бизнес-зона', callback_data='v6')
urlButton7 = InlineKeyboardButton(text='Паблик-толк с\nИгорем Асановым', callback_data='v7')
urlButton8 = InlineKeyboardButton(text='Несекретные материалы', callback_data='v8')
urlButton9 = InlineKeyboardButton(text='Стенды информации', callback_data='v9')
urlButton11 = InlineKeyboardButton(text='Викторины', callback_data='v11')
urlButton12 = InlineKeyboardButton(text='Квест "Зачетка абитуриента"', callback_data='v12')
urlButton13 = InlineKeyboardButton(text='Художественная школа "Полиграф"', callback_data='v13')
urlButton14 = InlineKeyboardButton(text='Киберспортивные танцы', callback_data='v14')
#urlButton10 = InlineKeyboardButton(text='WorkShop', callback_data='v10')

urlkb.add(urlButton1, urlButton7, urlButton9, urlButton4, urlButton3, urlButton2, urlButton5, urlButton11, urlButton6, urlButton8, urlButton12, urlButton13, urlButton14)


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'v3')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Узнать всё о поступлении, ты сможешь в холле корпуса А')

    cursor.execute("SELECT fotka, innffaa, fcam, map FROM ti WHERE korpus = 3")
    result = cursor.fetchone()

    if result:
        fotka, innffaa, fcam, map = result
        # Отправляем фотографию и текст

        await bot.send_message(callback_query.from_user.id, map)
        await asyncio.sleep(0.5)
        await bot.send_photo(callback_query.from_user.id, photo=fcam)
        await asyncio.sleep(0.5)
        await bot.send_message(callback_query.from_user.id, innffaa)
        await asyncio.sleep(0.5)
        await bot.send_photo(callback_query.from_user.id, photo=fotka)
    else:
        await bot.send_message(callback_query.from_user.id, 'Данные о маршруте не найдены.')

    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'v14')
async def handle_tok1(callback_query: types.CallbackQuery):

    cursor.execute("SELECT fotka, innffaa, fcam, map FROM ti WHERE korpus = 41")
    result = cursor.fetchone()

    if result:
        fotka, innffaa, fcam, map = result
        # Отправляем фотографию и текст

        await bot.send_message(callback_query.from_user.id, map)
        await asyncio.sleep(0.5)
        await bot.send_photo(callback_query.from_user.id, photo=fcam)
        await asyncio.sleep(0.5)
        await bot.send_message(callback_query.from_user.id, innffaa)
        await asyncio.sleep(0.5)
        await bot.send_photo(callback_query.from_user.id, photo=fotka)
    else:
        await bot.send_message(callback_query.from_user.id, 'Данные о маршруте не найдены.')

    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'v12')
async def handle_tok1(callback_query: types.CallbackQuery):

    cursor.execute("SELECT fotka, innffaa, fcam, map FROM ti WHERE korpus = 12")
    result = cursor.fetchone()

    if result:
        fotka, innffaa, fcam, map = result
        # Отправляем фотографию и текст

        await bot.send_message(callback_query.from_user.id, map)
        await asyncio.sleep(0.5)
        await bot.send_photo(callback_query.from_user.id, photo=fcam)
        await asyncio.sleep(0.5)
        await bot.send_message(callback_query.from_user.id, innffaa)
        await asyncio.sleep(0.5)
        await bot.send_photo(callback_query.from_user.id, photo=fotka)
    else:
        await bot.send_message(callback_query.from_user.id, 'Данные о маршруте не найдены.')

    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'v13')
async def handle_tok1(callback_query: types.CallbackQuery):


    cursor.execute("SELECT fotka, innffaa, fcam, map FROM ti WHERE korpus = 13")
    result = cursor.fetchone()

    if result:
        fotka, innffaa, fcam, map = result
        # Отправляем фотографию и текст

        await bot.send_message(callback_query.from_user.id, map)
        await asyncio.sleep(0.5)
        await bot.send_photo(callback_query.from_user.id, photo=fcam)
        await asyncio.sleep(0.5)
        await bot.send_message(callback_query.from_user.id, innffaa)
        await asyncio.sleep(0.5)
        await bot.send_photo(callback_query.from_user.id, photo=fotka)
    else:
        await bot.send_message(callback_query.from_user.id, 'Данные о маршруте не найдены.')

    await bot.answer_callback_query(callback_query.id)

'''@dp.callback_query_handler(lambda callback_query: callback_query.data == 'v10')
async def handle_tok1(callback_query: types.CallbackQuery):
    cursor.execute("SELECT fotka, innffaa, fcam, map FROM ti WHERE korpus = 10")
    result = cursor.fetchone()

    if result:
        fotka, innffaa, fcam, map = result
        # Отправляем фотографию и текст

        await bot.send_message(callback_query.from_user.id, map)
        await bot.send_photo(callback_query.from_user.id, photo=fcam)
        await bot.send_message(callback_query.from_user.id, innffaa)
        await bot.send_photo(callback_query.from_user.id, photo=fotka)
    else:
        await bot.send_message(callback_query.from_user.id, 'Данные о маршруте не найдены.')

    await bot.answer_callback_query(callback_query.id)'''

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'v11')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Ты можешь поучаствовать сразу в нескольких викторинах:\nв холле корпуса А пройдут\n«Интеллектуальная викторина о научных открытиях на стенде СНО», «Викторина по английскому языку»\nа также в аудитории А112а\n«Викторина от центра проектной деятельности»')

    cursor.execute("SELECT fotka, innffaa, fcam, map FROM ti WHERE korpus = 111")
    result = cursor.fetchone()

    if result:
        fotka, innffaa, fcam, map = result
        # Отправляем фотографию и текст

        await bot.send_message(callback_query.from_user.id, map)
        await asyncio.sleep(0.5)
        await bot.send_photo(callback_query.from_user.id, photo=fcam)
        await asyncio.sleep(0.5)
        await bot.send_message(callback_query.from_user.id, innffaa)
        await asyncio.sleep(0.5)
        await bot.send_photo(callback_query.from_user.id, photo=fotka)
    else:
        await bot.send_message(callback_query.from_user.id, 'Данные о маршруте не найдены.')

    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'v8')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Здесь ты сможешь узнать всё о поступлении, а также об изменениях в ЕГЭ по физике, русскому языку, математике, литературе.')

    cursor.execute("SELECT fotka, innffaa, fcam, map FROM ti WHERE korpus = 3")
    result = cursor.fetchone()

    if result:
        fotka, innffaa, fcam, map = result
        # Отправляем фотографию и текст

        await bot.send_message(callback_query.from_user.id, map)
        await asyncio.sleep(0.5)
        await bot.send_photo(callback_query.from_user.id, photo=fcam)
        await asyncio.sleep(0.5)
        await bot.send_message(callback_query.from_user.id, innffaa)
        await asyncio.sleep(0.5)
        await bot.send_photo(callback_query.from_user.id, photo=fotka)
    else:
        await bot.send_message(callback_query.from_user.id, 'Данные о маршруте не найдены.')

    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'v7')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Паблик-толк с блогером в сфере автоспорта Игорем Асановым.\n\n🤔Задумывались о том, как превратить своё хобби в профессию?\n\nНа День открытых дверей мы пригласили документалиста и блогера в сфере автоспорта Игоря Асанова. На паблик-токе мы обсудим, как сочетать несочетаемое и выбрать профессию по интересам так, чтобы потом не разочароваться. Начинайте готовить свои вопросы!\n\nКонечно, познакомим вас с флагманскими проектами, покажем студенческие разработки на выставке проектной деятельности и расскажем про науку и внеучебную жизнь в университете.\n\nУвидимся в 11:00 в аудитории А200!')

    cursor.execute("SELECT fotka, innffaa, fcam, map FROM ti WHERE korpus = 7")
    result = cursor.fetchone()

    if result:
        fotka, innffaa, fcam, map = result
        # Отправляем фотографию и текст
        await asyncio.sleep(0.5)
        await bot.send_message(callback_query.from_user.id, map)
        await asyncio.sleep(0.5)
        await bot.send_photo(callback_query.from_user.id, photo=fcam)
        await asyncio.sleep(0.5)
        await bot.send_message(callback_query.from_user.id, innffaa)
        await asyncio.sleep(0.5)
        await bot.send_photo(callback_query.from_user.id, photo=fotka)
    else:
        await bot.send_message(callback_query.from_user.id, 'Данные о маршруте не найдены.')

    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'v4')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Здесь помимо просмотра выставки проектов, вы также сможете поучаствовать в увлекательных викторинах и мастер-классах от центра проектной деятельности.')

    cursor.execute("SELECT fotka, innffaa, fcam, map FROM ti WHERE korpus = 4")
    result = cursor.fetchone()

    if result:
        fotka, innffaa, fcam, map = result
        # Отправляем фотографию и текст

        await bot.send_message(callback_query.from_user.id, map)
        await bot.send_photo(callback_query.from_user.id, photo=fcam)
        await bot.send_message(callback_query.from_user.id, innffaa)
        await bot.send_photo(callback_query.from_user.id, photo=fotka)
    else:
        await bot.send_message(callback_query.from_user.id, 'Данные о маршруте не найдены.')

    await bot.answer_callback_query(callback_query.id)


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'v5')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Посетить «Выставочные зоны» можно в аудиториях Б303 и Б410')

    cursor.execute("SELECT fotka, innffaa, fcam, map FROM ti WHERE korpus = 5")
    result = cursor.fetchone()

    if result:
        fotka, innffaa, fcam, map = result
        # Отправляем фотографию и текст

        await bot.send_message(callback_query.from_user.id, map)
        await bot.send_photo(callback_query.from_user.id, photo=fcam)
        await bot.send_message(callback_query.from_user.id, innffaa)
        await bot.send_photo(callback_query.from_user.id, photo=fotka)
    else:
        await bot.send_message(callback_query.from_user.id, 'Данные о маршруте не найдены.')

    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'v6')
async def handle_tok1(callback_query: types.CallbackQuery):

    cursor.execute("SELECT fotka, innffaa, fcam, map FROM ti WHERE korpus = 6")
    result = cursor.fetchone()

    if result:
        fotka, innffaa, fcam, map = result
        # Отправляем фотографию и текст

        await bot.send_message(callback_query.from_user.id, map)
        await bot.send_photo(callback_query.from_user.id, photo=fcam)
        await bot.send_message(callback_query.from_user.id, innffaa)
        await bot.send_photo(callback_query.from_user.id, photo=fotka)
    else:
        await bot.send_message(callback_query.from_user.id, 'Данные о маршруте не найдены.')

    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'v9')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Cтенды информации:\n«Инженерная школа»\n«Курсы подготовки к ЕГЭ»\n«Договорной отдел»\nнаходятся в аудитории - В104\n\nCтенды информации:\n«Профсоюзной организации работников и обучающихся»\n«Управления студенческого городка»\n«Управления по международной интеграции и работе с иностранными студентами»\nнаходятся в аудитории - В105')

    cursor.execute("SELECT fotka, innffaa, fcam, map FROM ti WHERE korpus = 9")
    result = cursor.fetchone()

    if result:
        fotka, innffaa, fcam, map = result
        # Отправляем фотографию и текст

        await bot.send_message(callback_query.from_user.id, map)
        await bot.send_photo(callback_query.from_user.id, photo=fcam)

        await bot.send_message(callback_query.from_user.id, innffaa)
        await bot.send_photo(callback_query.from_user.id, photo=fotka)
    else:
        await bot.send_message(callback_query.from_user.id, 'Данные о маршруте не найдены.')

    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(text='v2')
async def v2_call(callback : types.CallbackQuery):
	await callback.message.answer('Выбери мастер-класс по интересующему тебя направлению:', reply_markup=inm)
	await callback.answer()

# Если выбор пал на офиц часть
inm = InlineKeyboardMarkup(row_width=1)
sm1 = InlineKeyboardButton(text='Арт, дизайн и медиа', callback_data='m1')
sm2 = InlineKeyboardButton(text='Урбанистика', callback_data='m2')
sm4 = InlineKeyboardButton(text='Бизнес', callback_data='m4')
sm5 = InlineKeyboardButton(text='Информационные технологии', callback_data='m5')
sm6 = InlineKeyboardButton(text='Транспорт, цифра, логистика', callback_data='m6')
sm3 = InlineKeyboardButton(text='Экология и технологии жизни', callback_data='m3')
sm7 = InlineKeyboardButton(text='Технологии, материалы и производство', callback_data='m7')

inm.add(sm4, sm2, sm1, sm5, sm6, sm3, sm7)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'm1')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Мастер-классы по направлению «Арт, дизайн и медиа» проходят в аудиториях Б303, Б306, Б309, Б310, Б410')

    cursor.execute("SELECT fotka, innffaa, fcam, map FROM ti WHERE korpus = 21")
    result = cursor.fetchone()

    if result:
        fotka, innffaa, fcam, map = result
        # Отправляем фотографию и текст

        await bot.send_message(callback_query.from_user.id, map)
        await bot.send_photo(callback_query.from_user.id, photo=fcam)
        await bot.send_message(callback_query.from_user.id, innffaa)
        await bot.send_photo(callback_query.from_user.id, photo=fotka)
    else:
        await bot.send_message(callback_query.from_user.id, 'Данные о маршруте не найдены.')

    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'm2')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Мастер-классы по направлению «Урбанистика» от факультета урбанистики и городского хозяйства проходят в аудитории Б307')

    cursor.execute("SELECT fotka, innffaa, fcam, map FROM ti WHERE korpus = 22")
    result = cursor.fetchone()

    if result:
        fotka, innffaa, fcam, map = result
        # Отправляем фотографию и текст

        await bot.send_message(callback_query.from_user.id, map)
        await bot.send_photo(callback_query.from_user.id, photo=fcam)
        await bot.send_message(callback_query.from_user.id, innffaa)
        await bot.send_photo(callback_query.from_user.id, photo=fotka)
    else:
        await bot.send_message(callback_query.from_user.id, 'Данные о маршруте не найдены.')

    await bot.answer_callback_query(callback_query.id)


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'm4')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Мастер-классы по направлению «Бизнес» от факультета экономики и управления проходят в аудитории Б311')

    cursor.execute("SELECT fotka, innffaa, fcam, map FROM ti WHERE korpus = 24")
    result = cursor.fetchone()

    if result:
        fotka, innffaa, fcam, map = result
        # Отправляем фотографию и текст

        await bot.send_message(callback_query.from_user.id, map)
        await bot.send_photo(callback_query.from_user.id, photo=fcam)
        await bot.send_message(callback_query.from_user.id, innffaa)
        await bot.send_photo(callback_query.from_user.id, photo=fotka)
    else:
        await bot.send_message(callback_query.from_user.id, 'Данные о маршруте не найдены.')

    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'm5')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Мастер-классы по направлению «Информационные технологии» проходят в аудитории Н305')

    cursor.execute("SELECT fotka, innffaa, fcam, map FROM ti WHERE korpus = 25")
    result = cursor.fetchone()

    if result:
        fotka, innffaa, fcam, map = result
        # Отправляем фотографию и текст

        await bot.send_message(callback_query.from_user.id, map)
        await bot.send_photo(callback_query.from_user.id, photo=fcam)
        await bot.send_message(callback_query.from_user.id, innffaa)
        await bot.send_photo(callback_query.from_user.id, photo=fotka)
    else:
        await bot.send_message(callback_query.from_user.id, 'Данные о маршруте не найдены.')

    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'm3')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Мастер-класс по направлению «Экология и технологии жизни» от Факультета химической технологии и биотехнологии пройдёт в аудитории Б303.')

    cursor.execute("SELECT fotka, innffaa, fcam, map FROM ti WHERE korpus = 23")
    result = cursor.fetchone()

    if result:
        fotka, innffaa, fcam, map = result
        # Отправляем фотографию и текст

        await bot.send_message(callback_query.from_user.id, map)
        await bot.send_photo(callback_query.from_user.id, photo=fcam)
        await bot.send_message(callback_query.from_user.id, innffaa)
        await bot.send_photo(callback_query.from_user.id, photo=fotka)
    else:
        await bot.send_message(callback_query.from_user.id, 'Данные о маршруте не найдены.')

    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'm7')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Мастер-класс по направлению «Технологии, материалы и производство» от факультета химической технологии и биотехнологии, а также факультета машиностроения и полиграфического института пройдёт в аудитории Б303.')

    cursor.execute("SELECT fotka, innffaa, fcam, map FROM ti WHERE korpus = 10") #43 по логике, но маршрут повторяется с 10 строкой
    result = cursor.fetchone()

    if result:
        fotka, innffaa, fcam, map = result
        # Отправляем фотографию и текст

        await bot.send_message(callback_query.from_user.id, map)
        await bot.send_photo(callback_query.from_user.id, photo=fcam)
        await bot.send_message(callback_query.from_user.id, innffaa)
        await bot.send_photo(callback_query.from_user.id, photo=fotka)
    else:
        await bot.send_message(callback_query.from_user.id, 'Данные о маршруте не найдены.')

    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'm6')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Мастер-класс по направлению «Транспорт, цифра, логистика» от транспортного факультета пройдут в аудитории Б411')

    cursor.execute("SELECT fotka, innffaa, fcam, map FROM ti WHERE korpus = 26")
    result = cursor.fetchone()

    if result:
        fotka, innffaa, fcam, map = result
        # Отправляем фотографию и текст

        await bot.send_message(callback_query.from_user.id, map)
        await bot.send_photo(callback_query.from_user.id, photo=fcam)
        await bot.send_message(callback_query.from_user.id, innffaa)
        await bot.send_photo(callback_query.from_user.id, photo=fotka)
    else:
        await bot.send_message(callback_query.from_user.id, 'Данные о маршруте не найдены.')

    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(text='v1')
async def v2_call(callback : types.CallbackQuery):
	await callback.message.answer('Выбери, что хочешь посетить:', reply_markup=inkb)
	await callback.answer()


# Если выбор пал на офиц часть
inkb = InlineKeyboardMarkup(row_width=1)
s1 = InlineKeyboardButton(text='Официальная часть в А200', callback_data='w1')
#s4 = InlineKeyboardButton(text='Трансляция официальной части', callback_data='w4')
s2 = InlineKeyboardButton(text='Встреча с деканом факультета', callback_data='w2')
s3 = InlineKeyboardButton(text='Встреча с директором института', callback_data='w3')

inkb.add(s1, s2, s3)
#официальная часть
@dp.callback_query_handler(lambda callback_query: callback_query.data == 'w1')
async def handle_tok1(callback_query: types.CallbackQuery):

    cursor.execute("SELECT fotka, innffaa, fcam, map FROM ti WHERE korpus = 11")
    result = cursor.fetchone()

    if result:
        fotka, innffaa, fcam, map = result
        # Отправляем фотографию и текст

        await bot.send_message(callback_query.from_user.id, map)
        await bot.send_photo(callback_query.from_user.id, photo=fcam)
        await bot.send_message(callback_query.from_user.id, innffaa)
        await bot.send_photo(callback_query.from_user.id, photo=fotka)
    else:
        await bot.send_message(callback_query.from_user.id, 'Данные о маршруте не найдены.')

    await bot.answer_callback_query(callback_query.id)

'''@dp.callback_query_handler(lambda callback_query: callback_query.data == 'w4')
async def handle_tok1(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Трансляция официальной части будет проходить в аудиториях: Б303 и Б404')

    cursor.execute("SELECT fotka, innffaa, fcam, map FROM ti WHERE korpus = 14")
    result = cursor.fetchone()

    if result:
        fotka, innffaa, fcam, map = result
        # Отправляем фотографию и текст

        await bot.send_message(callback_query.from_user.id, map)
        await bot.send_photo(callback_query.from_user.id, photo=fcam)
        await bot.send_message(callback_query.from_user.id, innffaa)
        await bot.send_photo(callback_query.from_user.id, photo=fotka)
    else:
        await bot.send_message(callback_query.from_user.id, 'Данные о маршруте не найдены.')

    await bot.answer_callback_query(callback_query.id)'''


@dp.callback_query_handler(text='w2')
async def v2_call(callback : types.CallbackQuery):
	await callback.message.answer('Выбери с деканом какого факультета ты хочешь встретиться:', reply_markup=inw)
	await callback.answer()

inw = InlineKeyboardMarkup(row_width=1)
sw1 = InlineKeyboardButton(text='Машиностроение', callback_data='ww1')
sw2 = InlineKeyboardButton(text='Урбанистика и \n'
                                'городское хозяйство', callback_data='ww2')
sw3 = InlineKeyboardButton(text='Химические технологии \n'
                                'и беотехнологии', callback_data='ww3')
sw4 = InlineKeyboardButton(text='Экономика и управление', callback_data='ww4')
sw5 = InlineKeyboardButton(text='Информационные технологии', callback_data='ww5')
sw6 = InlineKeyboardButton(text='Транспортный факультет', callback_data='ww6')

inw.add(sw1, sw2, sw3, sw4, sw5, sw6)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'ww1')
async def handle_tok1(callback_query: types.CallbackQuery):

    cursor.execute("SELECT fotka, innffaa, fcam, map FROM ti WHERE korpus = 121")
    result = cursor.fetchone()

    if result:
        fotka, innffaa, fcam, map = result
        # Отправляем фотографию и текст

        await bot.send_message(callback_query.from_user.id, map)
        await bot.send_photo(callback_query.from_user.id, photo=fcam)
        await bot.send_message(callback_query.from_user.id, innffaa)
        await bot.send_photo(callback_query.from_user.id, photo=fotka)
    else:
        await bot.send_message(callback_query.from_user.id, 'Данные о маршруте не найдены.')

    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'ww2')
async def handle_tok1(callback_query: types.CallbackQuery):

    cursor.execute("SELECT fotka, innffaa, fcam, map FROM ti WHERE korpus = 122")
    result = cursor.fetchone()

    if result:
        fotka, innffaa, fcam, map = result
        # Отправляем фотографию и текст
        await bot.send_message(callback_query.from_user.id, map)
        await bot.send_photo(callback_query.from_user.id, photo=fcam)
        await bot.send_message(callback_query.from_user.id, innffaa)
        await bot.send_photo(callback_query.from_user.id, photo=fotka)
    else:
        await bot.send_message(callback_query.from_user.id, 'Данные о маршруте не найдены.')

    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'ww3')
async def handle_tok1(callback_query: types.CallbackQuery):

    cursor.execute("SELECT fotka, innffaa, fcam, map FROM ti WHERE korpus = 123")
    result = cursor.fetchone()

    if result:
        fotka, innffaa, fcam, map = result
        # Отправляем фотографию и текст

        await bot.send_message(callback_query.from_user.id, map)
        await bot.send_photo(callback_query.from_user.id, photo=fcam)
        await bot.send_message(callback_query.from_user.id, innffaa)
        await bot.send_photo(callback_query.from_user.id, photo=fotka)
    else:
        await bot.send_message(callback_query.from_user.id, 'Данные о маршруте не найдены.')

    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'ww4')
async def handle_tok1(callback_query: types.CallbackQuery):

    cursor.execute("SELECT fotka, innffaa, fcam, map FROM ti WHERE korpus = 124")
    result = cursor.fetchone()

    if result:
        fotka, innffaa, fcam, map = result
        # Отправляем фотографию и текст
        await bot.send_message(callback_query.from_user.id, map)
        await bot.send_photo(callback_query.from_user.id, photo=fcam)
        await bot.send_message(callback_query.from_user.id, innffaa)
        await bot.send_photo(callback_query.from_user.id, photo=fotka)
    else:
        await bot.send_message(callback_query.from_user.id, 'Данные о маршруте не найдены.')

    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'ww5')
async def handle_tok1(callback_query: types.CallbackQuery):

    cursor.execute("SELECT fotka, innffaa, fcam, map FROM ti WHERE korpus = 125")
    result = cursor.fetchone()

    if result:
        fotka, innffaa, fcam, map = result
        # Отправляем фотографию и текст

        await bot.send_message(callback_query.from_user.id, map)
        await bot.send_photo(callback_query.from_user.id, photo=fcam)
        await bot.send_message(callback_query.from_user.id, innffaa)
        await bot.send_photo(callback_query.from_user.id, photo=fotka)
    else:
        await bot.send_message(callback_query.from_user.id, 'Данные о маршруте не найдены.')

    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'ww6')
async def handle_tok1(callback_query: types.CallbackQuery):

    cursor.execute("SELECT fotka, innffaa, fcam, map FROM ti WHERE korpus = 126")
    result = cursor.fetchone()

    if result:
        fotka, innffaa, fcam, map = result
        # Отправляем фотографию и текст
        await bot.send_message(callback_query.from_user.id, map)
        await bot.send_photo(callback_query.from_user.id, photo=fcam)
        await bot.send_message(callback_query.from_user.id, innffaa)
        await bot.send_photo(callback_query.from_user.id, photo=fotka)
    else:
        await bot.send_message(callback_query.from_user.id, 'Данные о маршруте не найдены.')

    await bot.answer_callback_query(callback_query.id)


@dp.callback_query_handler(text='w3')
async def v2_call(callback : types.CallbackQuery):
	await callback.message.answer('Выбери с директором какого института ты хочешь встретиться:', reply_markup=ynw)
	await callback.answer()

ynw = InlineKeyboardMarkup(row_width=1)
yw1 = InlineKeyboardButton(text='Полиграфический институт', callback_data='yw1')
yw2 = InlineKeyboardButton(text='Институт графики и искусства\n'
                                'книги имении В.А. Фаворского', callback_data='yw2')
yw3 = InlineKeyboardButton(text='Институт издательского дела\n'
                                'и журналистики', callback_data='yw3')

ynw.add(yw1, yw2, yw3)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'yw1')
async def handle_tok1(callback_query: types.CallbackQuery):

    cursor.execute("SELECT fotka, innffaa, fcam, map FROM ti WHERE korpus = 131")
    result = cursor.fetchone()

    if result:
        fotka, innffaa, fcam, map = result
        # Отправляем фотографию и текст
        await bot.send_message(callback_query.from_user.id, map)
        await bot.send_photo(callback_query.from_user.id, photo=fcam)
        await bot.send_message(callback_query.from_user.id, innffaa)
        await bot.send_photo(callback_query.from_user.id, photo=fotka)
    else:
        await bot.send_message(callback_query.from_user.id, 'Данные о маршруте не найдены.')

    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'yw2')
async def handle_tok1(callback_query: types.CallbackQuery):

    cursor.execute("SELECT fotka, innffaa, fcam, map FROM ti WHERE korpus = 132")
    result = cursor.fetchone()

    if result:
        fotka, innffaa, fcam, map = result
        # Отправляем фотографию и текст
        await bot.send_message(callback_query.from_user.id, map)
        await bot.send_photo(callback_query.from_user.id, photo=fcam)
        await bot.send_message(callback_query.from_user.id, innffaa)
        await bot.send_photo(callback_query.from_user.id, photo=fotka)
    else:
        await bot.send_message(callback_query.from_user.id, 'Данные о маршруте не найдены.')

    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'yw3')
async def handle_tok1(callback_query: types.CallbackQuery):

    cursor.execute("SELECT fotka, innffaa, fcam, map FROM ti WHERE korpus = 133")
    result = cursor.fetchone()

    if result:
        fotka, innffaa, fcam, map = result
        # Отправляем фотографию и текст
        await bot.send_message(callback_query.from_user.id, map)
        await bot.send_photo(callback_query.from_user.id, photo=fcam)
        await bot.send_message(callback_query.from_user.id, innffaa)
        await bot.send_photo(callback_query.from_user.id, photo=fotka)
    else:
        await bot.send_message(callback_query.from_user.id, 'Данные о маршруте не найдены.')

    await bot.answer_callback_query(callback_query.id)



'''if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(scheduler())'''

executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
# Запуск бота
