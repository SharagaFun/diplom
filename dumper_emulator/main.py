import asyncio
import websockets
import logging
import os
import json
from datetime import datetime, timedelta
import random

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def generate_users(num_users):
    users = []
    for i in range(num_users):
        user = {
            "ID": random.randint(100000000, 999999999),
            "Username": None,
            "FirstName": f"FirstName{i}",
            "LastName": f"LastName{i}",
            "PhoneNumber": f"+{random.randint(1000000000, 9999999999)}",
            "IsBot": False,
            "IsFake": False,
            "IsScam": False,
            "IsVerified": random.choice([False, True]),
            "IsPremium": False,
            "IsDeleted": False,
            "UpdatedAt": (datetime.now() + timedelta(days=random.randint(1, 100))).isoformat()+'Z'
        }
        users.append(user)
    
    with open('/root/history/users', 'w') as f:
        for user in users:
            f.write(json.dumps(user) + "\n")


async def dumper_emulator(websocket, path):
    # Отправляем запрос на ввод номера телефона
    await websocket.send("Enter phone number:")
    phone_number = await websocket.recv()
    logger.info(f"Received phone number: {phone_number}")

    # Отправляем запрос на ввод кода
    await websocket.send("Enter code:")
    code = await websocket.recv()
    logger.info(f"Received code: {code}")

    # Отправляем запрос на ввод пароля
    await websocket.send("Enter password:")
    password = await websocket.recv()
    logger.info(f"Received password: {password}")

    # После получения всех данных, отправляем подтверждение успешного входа
    await websocket.send("Login success")
    
    await generate_users(10)
    
async def main():
    await generate_users(10)
    # Запускаем сервер на порту 8080
    async with websockets.serve(dumper_emulator, "0.0.0.0", 8080):
        await asyncio.Future()  # Запускаем сервер бесконечно

if __name__ == "__main__":
    os.makedirs('/root/history', exist_ok=True)
    asyncio.run(main())

