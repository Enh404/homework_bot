import logging
import os
import sys
import time
import requests
import telegram

from dotenv import load_dotenv
from exceptions import exceptions

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    """Отправка сообщения в Telegram чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.info('Бот успешно отправил сообщение')
    except Exception as error:
        logging.error(f'Не удалось отправить сообщение в Telegram: {error}')


def get_api_answer(current_timestamp):
    """Выполнение запроса к эндпоинту API-сервиса."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    except ConnectionError as exc:
        logging.error(f'Ошибка при запросе к основному API: {exc}')
    if response.status_code != 200:
        error = f'Неудовлетворительный статус ответа: {response.status_code}'
        raise exceptions.BadResponseStatus(error)
    return response.json()


def check_response(response):
    """Проверка ответа API на корректность."""
    response = dict(response)
    if not isinstance(response, dict):
        error = f'Response не является словарем {response}'
        raise exceptions.WrongTypeResponse(error)
    if 'homeworks' not in response:
        error = f'Ключа homeworks в ответе нет: {response}'
        raise exceptions.WrongKeyHomeworks(error)
    homework = response['homeworks']
    if not isinstance(homework, list):
        error = 'Homework не является списком'
        raise TypeError(error)
    if not homework:
        error = f'Список {homework[0]} пуст'
        raise exceptions.EmptyValue(error)
    logging.info('Status of homework update')
    return homework


def parse_status(homework):
    """Информация о статусе домашней работы."""
    if not isinstance(homework, dict):
        error = 'Homework не является словарем'
        raise TypeError(error)
    if 'homework_name' not in homework:
        error = 'Ключ homework_name отсутствует'
        raise KeyError(error)
    if 'status' not in homework:
        error = 'Ключ status отсутствует'
        raise KeyError(error)
    homework_name = homework['homework_name']
    homework_status = homework['status']
    if homework_status not in HOMEWORK_STATUSES:
        error = f'Неизвестный статус: {homework_status}'
        raise exceptions.UnknownStatusHW(error)
    verdict = HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверка доступности переменных окружения."""
    if not PRACTICUM_TOKEN:
        logging.critical(
            "Отсутствует обязательная переменная окружения:"
            "'PRACTICUM_TOKEN' Программа принудительно остановлена.")
        return False
    if not TELEGRAM_TOKEN:
        logging.critical(
            "Отсутствует обязательная переменная окружения:"
            "'TELEGRAM_TOKEN' Программа принудительно остановлена.")
        return False
    if not TELEGRAM_CHAT_ID:
        logging.critical(
            "Отсутствует обязательная переменная окружения:"
            "'TELEGRAM_CHAT_ID' Программа принудительно остановлена.")
        return False
    return True


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        sys.exit()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time() - 30 * 24 * 60 * 60)
    status = ''
    while True:
        try:
            response = get_api_answer(current_timestamp)
            if check_response(response):
                homework = check_response(response)
                message = parse_status(homework[0])
                if message != status:
                    send_message(bot, message)
                    status = message
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            if message != status:
                send_message(bot, message)
                status = message
            logging.error(error, exc_info=True)
            continue
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s %(levelname)s %(name)s %(message)s',
        level=logging.INFO
    )
    main()
