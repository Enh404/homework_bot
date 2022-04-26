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

logging.basicConfig(
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    level=logging.INFO)


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
    response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    if response.status_code != 200:
        error = f'Неудовлетворительный статус ответа: {response.status_code}'
        raise exceptions.CheckResponseStatusException(error)
    return response.json()


def check_response(response):
    """Проверка ответа API на корректность."""
    if not response['homeworks']:
        error = f'Ключа homeworks в ответе нет: {response}'
        exceptions.CheckKeyHomeworksException(error)
    homework = response['homeworks']
    if not isinstance(homework, list):
        message = 'Неверный тип данных'
        raise TypeError(message)
    if not homework:
        error = f'Список {homework[0]} пуст'
        raise exceptions.EmptyValueException(error)
    logging.info('Status of homework update')
    return homework


def parse_status(homework):
    """Информация о статусе домашней работы."""
    if 'homework_name' and 'status' not in homework:
        error = 'Ключи homework_name и status отсутствуют'
        raise KeyError(error)
    else:
        homework_name = homework['homework_name']
        homework_status = homework['status']
    if homework_status not in HOMEWORK_STATUSES:
        error = f'Неизвестный статус: {homework_status}'
        raise exceptions.StatusHWException(error)
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
        error = 'Необходимые перменные отсутствуют.'
        logging.error(error, exc_info=True)
        sys.exit()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time() - 30 * 24 * 60 * 60)
    status = ''
    while True:
        try:
            response = get_api_answer(current_timestamp)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(f'Ошибка при запросе к основному API: {error}')
            time.sleep(RETRY_TIME)
            continue
        try:
            if check_response(response):
                homework = check_response(response)
                message = parse_status(homework[0])
                if message != status:
                    send_message(bot, message)
                    status = message
            current_timestamp = current_timestamp
            time.sleep(RETRY_TIME)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            if message != status:
                send_message(bot, message)
                status = message
            logging.error(error, exc_info=True)
            time.sleep(RETRY_TIME)
        finally:
            time.sleep(RETRY_TIME)
if __name__ == '__main__':
    main()
