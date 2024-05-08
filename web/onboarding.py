import subprocess
import requests
import json
from flask import Blueprint, request, session, redirect, url_for, render_template, flash, jsonify
from app import app
from models import UserAPI
from uuid import uuid4
from app import db
import asyncio
import aiohttp
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

onboarding_bp = Blueprint('onboarding', __name__)

ws_connection = None

async def get_ws_connection():
    try:
        global ws_connection
        if ws_connection is None or ws_connection.closed:
            logger.info("creating new ws connection")
            session = aiohttp.ClientSession()
            ws_connection = await session.ws_connect('ws://tg_history_dumper:8080/ws')
        return ws_connection
    except Exception as e:
        logger.info("error")
        logger.info(e)

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

async def send_data_to_dumper_service(data):
    try:
        ws_connection = await get_ws_connection()
        await ws_connection.send_str(data)  # Отправляем данные как простую строку
        response = await ws_connection.receive()  # Получаем ответ от сервера как текст
        logger.info(response)
        return response.data
    except Exception as e:
        logger.info("error")
        logger.info(e)

async def enter_phone(phone_number):
    try:
        ws_connection = await get_ws_connection()
        response = await ws_connection.receive()  # Получаем ответ от сервера как текст
        if "Enter phone number:" in response:
            logger.info("enter?")
            response = await send_data_to_dumper_service(phone_number)
        if "Enter code:" in response:
            return True
        else:
            return response
    except Exception as e:
        flash('Failed to submit phone number: {}'.format(e))
        return jsonify({'error': str(e)}), 500

@onboarding_bp.route('/submit_code', methods=['POST'])
async def submit_code():
    code = request.form['code']
    try:
        response = await send_data_to_dumper_service(code)
        if "Enter password:" in response:
            return render_template('enter_password.html')
        elif "Login success" in response:
            flash('Login successful')
            session['onboarding_completed'] = True
            return redirect(url_for('home'))
        else:
            flash('Failed to verify code')
            return redirect(url_for('onboarding.api_form'))
    except Exception as e:
        flash('Failed to submit code: {}'.format(e))
        return jsonify({'error': str(e)}), 500
    
@onboarding_bp.route('/submit_password', methods=['POST'])
async def submit_password():
    password = request.form['password']
    try:
        response = await send_data_to_dumper_service(password)
        if "Login success" in response:
            flash('Login successful')
            session['onboarding_completed'] = True
            return redirect(url_for('home'))
        else:
            flash('Failed to verify password')
            return redirect(url_for('onboarding.api_form'))
    except Exception as e:
        flash('Failed to submit code: {}'.format(e))
        return jsonify({'error': str(e)}), 500

@onboarding_bp.route('/submit_api_data', methods=['POST'])
async def submit_api_data():
    phone_number = request.form['phone_number']
    api_id = request.form['api_id']
    api_hash = request.form['api_hash']

    success, message = run_tg_history_dumper(api_id, api_hash, phone_number)
    if success:
        save_user_api_data(api_id, api_hash)
        await asyncio.sleep(2)
        phone_result = await enter_phone(phone_number)
        #flash('Your Telegram credentials have been verified.', 'success')
        if phone_result:
            return redirect(url_for('onboarding.enter_code'))
        else:
            flash('Wrong number')
            return redirect(url_for('onboarding.api_form'))
    else:
        flash(f'Failed to verify Telegram credentials. Error: {message}', 'error')
        return redirect(url_for('onboarding.api_form'))

@onboarding_bp.route('/enter_code')
def enter_code():
    return render_template('enter_code.html')

@onboarding_bp.route('/')
def onboarding():
    if session.get('onboarding_completed'):
        return redirect(url_for('home'))
    return render_template('onboarding.html')

@onboarding_bp.route('/api_form')
def api_form():
    return render_template('api_form.html')

def save_user_api_data(api_id, api_hash):
    new_user_api = UserAPI(api_id=api_id, api_hash=api_hash)
    db.session.add(new_user_api)
    db.session.commit()
