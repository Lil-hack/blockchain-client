import asyncio
import io
import logging
import os
import re
import threading
import time
from random import randint
from bit import PrivateKey
import qrcode as qrcode
import requests
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InputMediaDocument, KeyboardButton, ReplyKeyboardMarkup, ContentType
from urllib.request import urlopen
import json
import sqlite3
#--------------------Настройки бота-------------------------

# Ваш токен от BotFather
from aiogram.utils.executor import start_webhook

from btc_core import gen_address

TOKEN = 'YOUR TOKEN'

# Логирование
logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

try:
    conn = sqlite3.connect("my.db")  # или :memory: чтобы сохранить в RAM
    cursor = conn.cursor()
    # cursor.execute(
    #     "CREATE TABLE users (chatid INTEGER , name TEXT, balance INTEGER, btc_wallet TEXT, wif TEXT, btc_sent TEXT, state INTEGER)")
    # conn.commit()
except Exception as ex:
    print(ex)


#--------------------Метод при нажатии start-------------------------
@dp.message_handler(commands='start')
async def start(message: types.Message):
    # Добавляем нового пользователя
    reg_and_data_main(message)
    button = KeyboardButton('🌐 Ваш баланс')
    button2 = KeyboardButton('💳 Получить BTC')
    button3 = KeyboardButton('📤 Отправить BTC')
    kb = ReplyKeyboardMarkup(resize_keyboard=True).add(button).add(button2,button3)
    # Отправляем сообщение с кнопкой
    await bot.send_message(message.chat.id, '{}, Добро пожаловать в Blockchain.com!'.format(message.chat.first_name), reply_markup=kb)

def reg_and_data_main(message):

    sql_select = "SELECT * FROM users where chatid={}".format(message.chat.id)
    cursor.execute(sql_select)
    data = cursor.fetchone()
    if data is None:
        sql = "SELECT COUNT(*) FROM users "
        cursor.execute(sql)
        user = cursor.fetchone()  #
        address, wif= gen_address(user[0]+1)
        sql_insert = "INSERT INTO users VALUES ({}, '{}', 0,'{}','{}','no',0)".format(message.chat.id,
                                                                           message.chat.first_name,address,wif)

        cursor.execute(sql_insert)
        conn.commit()
        cursor.execute(sql_select)
        data = cursor.fetchone()
    return data


#--------------------Основная логика бота-------------------------
@dp.message_handler()
async def main_logic(message: types.Message):

    # Логика для пользователя
    # Получаем данные пользователя
    data=reg_and_data_main(message)

    if data is not None:
        if data[6]==0:
            if message.text == '💳 Получить BTC':
                img = qrcode.make(data[3])
                img.save('qr.jpg')

                await bot.send_message(message.chat.id, f'''💳 Ваш адрес биткойн кошелька:
    
*{data[3]}*''', parse_mode= "Markdown")
                await bot.send_photo(message.chat.id,photo=open('qr.jpg', 'rb'))

            if message.text == '🌐 Ваш баланс':
                url = f'https://blockchain.info/rawaddr/{data[3]}'
                x = requests.get(url)
                wallet = x.json()

                await bot.send_message(message.chat.id, f'''💰 *Итоговый баланс:* {format(wallet['final_balance'] / 100000000, '.9f')} BTC
    
*Всего получено:* {format(wallet['total_received'] / 100000000, '.9f')} BTC
*Всего отправлено:* {format(wallet['total_sent'] / 100000000, '.9f')} BTC

https://www.blockchain.com/ru/btc/address/{data[3]}''', parse_mode= "Markdown")

            if message.text == '📤 Отправить BTC':
                sql = "UPDATE users SET state = {} WHERE chatid = {}".format(1, message.chat.id)
                cursor.execute(sql)
                conn.commit()
                button = KeyboardButton('⬇️ Назад')
                kb = ReplyKeyboardMarkup(resize_keyboard=True).add(button)
                # Отправляем сообщение с кнопкой
                await bot.send_message(message.chat.id,'📤 Отправьте *адрес биткойн кошелька*, куда хотите перевести BTC (Например: 12rAUoBgNgCqBpKTHwKksrAwkHBFdq1yvr)',reply_markup=kb, parse_mode="Markdown")

        if data[6] == 1:
            if message.text == '⬇️ Назад':
                sql = "UPDATE users SET state = {} WHERE chatid = {}".format(0, message.chat.id)
                cursor.execute(sql)
                conn.commit()
                button = KeyboardButton('🌐 Ваш баланс')
                button2 = KeyboardButton('💳 Получить BTC')
                button3 = KeyboardButton('📤 Отправить BTC')
                kb = ReplyKeyboardMarkup(resize_keyboard=True).add(button).add(button2, button3)
                await bot.send_message(message.chat.id,'Вы вернулись в меню',reply_markup=kb)

            if message.text != '⬇️ Назад':
                result = re.match(r'^(?=.*[0-9])(?=.*[a-zA-Z])[\da-zA-Z]{27,34}$', message.text)

                if result is None:
                    mes = '''❗️*Ошибка*
Check that BTC wallet is entered correctly!'''
                    await bot.send_message(message.chat.id, mes, parse_mode="Markdown")
                else:
                    sql = "UPDATE users SET state = {} WHERE chatid = {}".format(2, message.chat.id)
                    cursor.execute(sql)
                    conn.commit()
                    sql = "UPDATE users SET btc_sent = '{}' WHERE chatid = {}".format(result.group(0), message.chat.id)
                    cursor.execute(sql)
                    conn.commit()
                    button = KeyboardButton('⬇️ Назад')
                    kb = ReplyKeyboardMarkup(resize_keyboard=True).add(button)
                    # Отправляем сообщение с кнопкой
                    await bot.send_message(message.chat.id, f'💰 Отправьте сумму, которую хотите перевести по адресу *{result.group(0)}* в BTC (Например: 0.0001). *Комиссия перевода 0.0001 BTC*',
                                           reply_markup=kb, parse_mode="Markdown")
        if data[6] == 2:
            if message.text == '⬇️ Назад':
                sql = "UPDATE users SET state = {} WHERE chatid = {}".format(0, message.chat.id)
                cursor.execute(sql)
                conn.commit()
                button = KeyboardButton('🌐 Ваш баланс')
                button2 = KeyboardButton('💳 Получить BTC')
                button3 = KeyboardButton('📤 Отправить BTC')
                kb = ReplyKeyboardMarkup(resize_keyboard=True).add(button).add(button2, button3)
                await bot.send_message(message.chat.id, 'Вы вернулись в меню', reply_markup=kb)

            if message.text != '⬇️ Назад':
                try:
                    sum=float(message.text)
                    url = f'https://blockchain.info/rawaddr/{data[3]}'
                    x = requests.get(url)
                    wallet = x.json()
                    if sum+10000<=wallet['final_balance'] / 100000000:
                        try:
                            my_key = PrivateKey(wif=data[4])
                            # Коммисия перевода, если поставить слишком маленькую, то транзакцию не примут
                            # И чем больше коммисия, тем быстрее пройдет перевод
                            fee = 10000
                            # Генерация транзакции
                            tx_hash = my_key.create_transaction([(data[5], sum, 'btc')], fee=fee, absolute_fee=True)
                            print(tx_hash)
                            url = 'https://blockchain.info/pushtx'
                            x = requests.post(url, data={'tx': tx_hash})
                            result = x.text
                            sql = "UPDATE users SET state = {} WHERE chatid = {}".format(0, message.chat.id)
                            cursor.execute(sql)
                            conn.commit()
                            button = KeyboardButton('🌐 Ваш баланс')
                            button2 = KeyboardButton('💳 Получить BTC')
                            button3 = KeyboardButton('📤 Отправить BTC')
                            kb = ReplyKeyboardMarkup(resize_keyboard=True).add(button).add(button2, button3)
                            await bot.send_message(message.chat.id,result, reply_markup=kb)
                        except Exception:
                            sql = "UPDATE users SET state = {} WHERE chatid = {}".format(0, message.chat.id)
                            cursor.execute(sql)
                            conn.commit()
                            button = KeyboardButton('🌐 Ваш баланс')
                            button2 = KeyboardButton('💳 Получить BTC')
                            button3 = KeyboardButton('📤 Отправить BTC')
                            kb = ReplyKeyboardMarkup(resize_keyboard=True).add(button).add(button2, button3)
                            await bot.send_message(message.chat.id, "⚠ Ошибка при выолнении транзакции", reply_markup=kb)
                    else:
                        await bot.send_message(message.chat.id, '⚠️  На вашем балансе недостаточно средств.')
                except ValueError:
                    await bot.send_message(message.chat.id, '⚠️Неправильно введена сумма отправления, попробуйте еще раз')

    else:
        await bot.send_message(message.chat.id, 'Нажмите /start')



#--------------------Запуск бота-------------------------
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

