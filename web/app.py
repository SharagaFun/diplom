from flask import Flask, render_template, request, redirect, url_for, session, jsonify, Talisman
from flask_babel import Babel
from flask_sqlalchemy import SQLAlchemy
import requests
from asgiref.wsgi import WsgiToAsgi
import json
import hashlib
import secrets
import os
from datetime import datetime
from flask import session
import time
import glob
import logging
import base64
from PIL import Image
from io import BytesIO
from flask_wtf import CSRFProtect

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
Talisman(app, content_security_policy=None)
asgi_app = WsgiToAsgi(app)
app.config['SECRET_KEY'] = os.urandom(24)
csrf = CSRFProtect(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@db/dbname'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
from models import *
with app.app_context():
    db.create_all()

# Создаем экземпляр Babel без инициализации с приложением
babel = Babel()

@app.context_processor
def inject_locale():
    return dict(get_locale=get_locale)

def get_locale():
    selected_language = session.get('language')
    if selected_language:
        return selected_language
    return request.accept_languages.best_match(['en', 'ru']) or 'en'

# Инициализация Babel с приложением и функцией выбора локали
babel.init_app(app, locale_selector=get_locale)

from onboarding import onboarding_bp
app.register_blueprint(onboarding_bp)

@app.route('/set_language/<lang>')
def set_language(lang):
    session['language'] = lang
    return redirect(url_for('onboarding.onboarding'))

@app.route('/home')
def home():
    #if session.get('onboarding_completed')!=True:
    #    return redirect(url_for('onboarding.onboarding')) #коментить при тестах через эмулятор
    file_path = '/root/history/users'
    time.sleep(1)
    try:
        # Убедитесь, что файл существует перед чтением
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                users=[]
                for line in file:
                    user = json.loads(line.strip())
                    main_part, fractional_part = user['UpdatedAt'].split('.')
                    fractional_part=fractional_part[:6]
                    user['UpdatedAt'] = f"{main_part}.{fractional_part}"
                    user['UpdatedAt'] = datetime.strptime(user['UpdatedAt'], "%Y-%m-%dT%H:%M:%S.%f")
                    users.append(user)
            return render_template('home_chats.html', users=users)
        else:
            return 'File does not exist.', 404
    except Exception as e:
        lol()
        # Логируем ошибку и возвращаем сообщение об ошибке
        return 'An error occurred while reading the file.', 500
    # Логика для главной страницы после онбординга
    #return 'Это главная страница. Онбординг завершен.'

@app.route('/process', methods=['POST'])
def process():
    user_ids = request.form.getlist('selected_users')
    response = {}

    if not user_ids:
        return jsonify({"error": "No user IDs provided"}), 400
    
    base_url = "http://127.0.0.1:8090/"
    links = []
    for user_id in user_ids:
        # Использование функции view_chat напрямую для генерации HTML
        html_content = view_chat(user_id)

        # Генерация случайного хеша для имени файла
        random_hash = secrets.token_hex(16)
        file_name = f"{random_hash}.html"
        file_path = os.path.join('/root/shared_chats', file_name)

        # Сохранение HTML в файл
        with open(file_path, 'w') as file:
            file.write(html_content)
        
        # Добавление пути к файлу в ответ
        chat_link = f"{base_url}{file_name}"
        links.append((user_id, chat_link))

    return render_template('links.html', links=links)



@app.route('/all_chats')
def all_chats():
    file_path = '/root/history/users'  # Путь к файлу с информацией о пользователях (чатах)
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                users = [json.loads(line.strip()) for line in file]
            return render_template('all_chats.html', users=users)
        else:
            return 'File does not exist.', 404
    except Exception as e:
        logger.error(f'An error occurred while reading the file: {e}')
        return 'An error occurred while reading the file.', 500

@app.route('/view_chat/<int:chat_id>')
def view_chat(chat_id):
    # Попытка найти файл истории чата по ID
    chat_history_pattern = f'/root/history/{chat_id}_*'
    chat_history_files = glob.glob(chat_history_pattern)
    logger.info(chat_history_files)
    
    
    if chat_history_files:
        chat_history_path = chat_history_files[0]  # Берем первый файл, если найдено несколько
        chat_name=chat_history_path.split('_')[1]
        try:
            with open(chat_history_path, 'r') as file:
                messages = [json.loads(line.strip()) for line in file]
                for message in messages:
                    if message.get('Media') and message['Media'].get('Photo'):
                        media = message['Media']['Photo']
                        photo_id = message["ID"]
                        photo_path = f"/root/history/files/{chat_id}_{chat_name}/{photo_id}_Media_photo.jpg"
                        if os.path.exists(photo_path):
                            # Кодировать файл в base64 и заменить во всех размерах, где есть поле "Bytes"
                            with Image.open(photo_path) as image:
                                buffered = BytesIO()
                                image.save(buffered, format="JPEG")
                                encoded_image =  base64.b64encode(buffered.getvalue()).decode('utf-8')
                            media['Sizes'][0]['Bytes'] = encoded_image
            return render_template('view_chat.html', messages=messages, chat_id=chat_id, chat_name=chat_name)
        except Exception as e:
            logger.error(f'An error occurred while reading the chat history: {e}')
            return 'An error occurred while reading the chat history.', 500
    else:
        return 'Chat history does not exist.', 404

@app.route('/summary', methods=['POST'])
def summary():
    data = request.json
    chat_id = data['chat_id']
    start_date = datetime.fromisoformat(data['start_date'])
    end_date = datetime.fromisoformat(data['end_date'])
    logger.info(start_date, end_date)
    # Загружаем информацию о пользователях
    users_file_path = '/root/history/users'
    users = {}
    try:
        if os.path.exists(users_file_path):
            with open(users_file_path, 'r') as users_file:
                for line in users_file:
                    user = json.loads(line.strip())
                    users[user['ID']] = user['FirstName']  # Сопоставляем UserID с FirstName
        logger.info(users)
    except Exception as e:
        logger.error(f'An error occurred while reading the users file: {e}')
        return 'An error occurred while reading the users file.', 500

    # Попытка найти файл истории чата по ID
    chat_history_pattern = f'/root/history/{chat_id}_*'
    chat_history_files = glob.glob(chat_history_pattern)
    summary_text = ""

    if chat_history_files:
        chat_history_path = chat_history_files[0]  # Берем первый файл, если найдено несколько
        try:
            with open(chat_history_path, 'r') as file:
                for line in file:
                    message = json.loads(line.strip())
                    message_date = datetime.fromtimestamp(message['Date'])
                    #logger.info(message_date,
                    #(start_date <= message_date <= end_date))
                    # Проверяем, что сообщение находится в выбранном временном диапазоне
                    if start_date <= message_date <= end_date:
                        user_id = message['PeerID']['UserID']
                        # Получаем имя пользователя из словаря или используем 'Unknown'
                        logger.info(user_id)
                        user_name = users.get(int(user_id)) if not message['Out'] else users.get(list(users.keys())[0])
                        # Форматируем сообщение как "Имя пользователя: сообщение"
                        summary_text += f"{user_name}: {message['Message']}\n"
            logger.info(summary_text)
            #return summary_text
        except Exception as e:
            logger.error(f'An error occurred while reading the chat history: {e}')
            return 'An error occurred while reading the chat history.', 500
    else:
        return 'Chat history does not exist.', 404
    # Отправляем summary_text на ручку Ollama
    ollama_url = 'http://ollama:11434/api/generate'
    prompt = "Это переписка двух людей в мессенджере. Постарайся написать ее краткое содержание на русском языке в паре-тройке предложений:\n" + summary_text
    payload = {
        "model": "starling-lm",
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(ollama_url, json=payload)
        response.raise_for_status()
        generated_text = response.json()
        logger.info(generated_text)
        return generated_text
    except requests.RequestException as e:
        logger.error(f'Error when calling Ollama API: {e}')
        return 'An error occurred while calling Ollama API.', 500

if __name__ == "__main__":
    
    app.run(debug=True)
    
