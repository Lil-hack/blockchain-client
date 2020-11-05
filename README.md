#Исходники и как запустить
Скачать исходники бота можно тут: github.com/Lil-hack/blockchain-client

Склонировав репозиторий, устанавливаем необходимые пакеты:

pip install -r requirements.txt

Некоторые библиотеки у меня не заработали на windows, так что лучше сразу запускать на linux.

В файле main.py заменяем ваш токен телеграм бота:

TOKEN = 'YOUR TOKEN'

В файле btc_core.py заменяем на вашу seed фразу:

seed = 'YOUR SEED'

И запускаем бота командой: python main.py

Работает на python 3.7.0 и выше.
