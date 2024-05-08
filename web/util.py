import logging
import argparse
#from onboarding import run_tg_history_dumper
import os
import requests
import json
import glob
import curses
from datetime import datetime, timezone

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def format_timestamp(unix_timestamp):
    return datetime.fromtimestamp(unix_timestamp, tz=timezone.utc).strftime('%d-%m-%Y %H:%M')

def parse_users(file_path):
    users = []
    try:
        with open(file_path, 'r') as file:
            users = [json.loads(line.strip()) for line in file]
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
    return users

def run_tg_history_dumper(api_id, api_hash, phone_number):
    url = 'http://tg_history_dumper:5001/run_dumper'
    payload = {
        "api_id": api_id,
        "api_hash": api_hash,
        "phone_number": phone_number
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        
        return data['success'], data.get('output', '')
    except requests.RequestException as e:
        return False, str(e)

def show_chat(stdscr, chat_id):
    # Попытка найти файл истории чата по ID
    #logger.info("chat_id")
    #logger.info(chat_id)
    chat_id=int(chat_id)
    chat_history_pattern = f'/root/history/{chat_id}_*'
    chat_history_files = glob.glob(chat_history_pattern)
    #logger.info(chat_history_files)
    stdscr.clear()  # Очищаем экран перед выводом новой информации
    
    if chat_history_files:
        chat_history_path = chat_history_files[0]  # Берем первый файл, если найдено несколько
        try:
            with open(chat_history_path, 'r') as file:
                messages = [json.loads(line.strip()) for line in file]
            #print(f"History for chat ID {chat_id}:")
            pad = curses.newpad(1000, 100)  # Создаем pad размером достаточным для большинства случаев
            y = 0
            max_y, max_x = stdscr.getmaxyx()
            users_file_path = '/root/history/users'
            users = {}
            if os.path.exists(users_file_path):
                with open(users_file_path, 'r') as users_file:
                    for line in users_file:
                        user = json.loads(line.strip())
                        users[user['ID']] = user['FirstName']  # Сопоставляем UserID с FirstName
            for message in messages:
                y = print_message_details(pad, y, message, users, max_y)
                if y >= max_y:
                    break  # Если достигли нижней границы экрана, прекращаем вывод

            # Управление скроллингом
            pad_pos = 0
            max_y, max_x = stdscr.getmaxyx()
            while True:
                pad.refresh(pad_pos, 0, 0, 0, max_y-1, max_x-1)
                key = stdscr.getch()
                if key == curses.KEY_DOWN:
                    pad_pos += 1
                elif key == curses.KEY_UP:
                    pad_pos -= 1
                elif key == 27:  # Код клавиши ESC
                    return  # Возвращаем управление в главный цикл
        except Exception as e:
            hui()
            print(f'An error occurred while reading the chat history: {e}')
    else:
        print('Chat history does not exist.')
    input()

def print_message_details(pad, y, message, users, max_y):
    if y >= max_y:  # Проверяем, не вышли ли мы за пределы экрана
        return y  # Возвращаем текущую позицию y, не увеличивая её

    user_id = message['PeerID'].get('UserID', None)
    user_name = users.get(int(user_id), 'Unknown') if user_id else 'Unknown'
    
    message_content = message.get('Message', '')
    date_formatted = format_timestamp(message['Date'])
    
    # Печатаем детали сообщения
    if y < max_y:
        pad.addstr(y, 0, f"[{date_formatted}] {user_name}: {message_content}")
        y += 1  # Перемещаемся на следующую строку
    
    #if message['Media'] and 'Media' in message and 'Photo' in message['Media']:
    #    if y < max_y:
    #        pad.addstr(y, 0, "This message includes a photo.")
    #        y += 1  # Дополнительная строка для медиа
    
    return y  # Возвращаем текущую позицию y после добавления текста

def load_users(file_path):
    users = {}
    if os.path.exists(file_path):
        with open(file_path, 'r') as users_file:
            for line in users_file:
                user = json.loads(line.strip())
                users[user['ID']] = user['FirstName']  # Сопоставляем UserID с FirstName
    return users


def display_chats(stdscr, users):
    # Инициализация curses
    curses.curs_set(0)  # Скрываем курсор
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)  # Устанавливаем цветовую схему
    current_row = 0  # Текущий выбранный ряд
    stdscr.clear()  # Очищаем экран перед выводом новой информации

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()  # Получаем размеры терминала
        for idx, user in enumerate(users):
            username = user.get('Username', 'None')
            line = f"{user['ID']} {username} {user['FirstName']} {user['LastName']}"
            x = max(0, width // 2 - len(line) // 2)  # Центрируем текст, ограничивая минимальное значение
            y = max(0, height // 2 - len(users) // 2 + idx)  # Расчет вертикальной позиции
            if y >= height:
                break  # Предотвращаем выход за пределы экрана по вертикали
            if idx == current_row:
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(y, x, line)
                stdscr.attroff(curses.color_pair(1))
            else:
                stdscr.addstr(y, x, line)

        stdscr.refresh()

        key = stdscr.getch()
        stdscr.addstr(0, 0, f"Key pressed: {key}   ")  # Показываем код нажатой клавиши
        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(users) - 1:
            current_row += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            show_chat(stdscr, users[current_row]['ID'])
            display_chats(stdscr, users)

        # Обновляем только измененные строки для снижения мерцания
        stdscr.noutrefresh()
        curses.doupdate()

def main():
    parser = argparse.ArgumentParser(description="Run the Telegram history dumper.")
    parser.add_argument("--update", action="store_true", help="Update the data.")
    parser.add_argument("--api_id", type=int, help="API ID for Telegram.")
    parser.add_argument("--api_hash", type=str, help="API Hash for Telegram.")
    parser.add_argument("--phone_number", type=str, help="Phone number associated with the Telegram account.")
    
    args = parser.parse_args()
    
    if args.update:
        if args.api_id and args.api_hash and args.phone_number:
            result = run_tg_history_dumper(args.api_id, args.api_hash, args.phone_number)
            print(result)
        else:
            print("Missing required parameters for updating.")
    elif not any([args.update, args.api_id, args.api_hash, args.phone_number]):
        file_path = '/root/history/users'
        if os.path.exists(file_path):
            users = parse_users(file_path)
            curses.wrapper(display_chats, users)
        else:
            print("File not found.")
    else:
        print("No action specified.")

if __name__ == "__main__":
    main()