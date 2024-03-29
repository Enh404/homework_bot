# Бот-ассистент

Telegram-бот, который обращается к API сервиса Практикум.Домашка и узнавает статус домашней работы: взята домашка в ревью, проверена ли она, а если проверена — то принял её ревьюер или вернул на доработку.

## Бот умеет:

- раз в 10 минут опрашивать API сервиса Практикум.Домашка и проверять статус отправленной на ревью домашней работы;

- при обновлении статуса анализировать ответ API и отправлять вам соответствующее уведомление в Telegram;

- логировать свою работу и сообщать вам о важных проблемах сообщением в Telegram.

## Запуск на ПК

Клонируем проект:

`git clone git@github.com:Enh404/homework_bot.git`

Переходим в папку с ботом.

`cd homework_bot`

Устанавливаем виртуальное окружение

`python -m venv venv`

Активируем виртуальное окружение

`source venv/Scripts/activate`

Устанавливаем зависимости

`pip install -r requirements.txt`

В консоле импортируем токены для ЯндексюПрактикум и для Телеграмм:
```
export PRACTICUM_TOKEN=<PRACTICUM_TOKEN>
export TELEGRAM_TOKEN=<TELEGRAM_TOKEN>
export CHAT_ID=<CHAT_ID>
```
Запускаем бота

`python homework.py`
