from flask import Flask, request, jsonify
import logging
from subprocess import Popen, PIPE
import json
import threading

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def run_process_and_log(api_id, api_hash):
    config = {
        "app_id": int(api_id),
        "app_hash": api_hash,
        "session_file_path": "tg.session",
        "media": [
            {"type": "user"}
        ]
    }
    
    # Создаем файл конфигурации для tg_history_dumper
    config_path = 'config.json'
    with open(config_path, 'w') as file:
        json.dump(config, file)
    
    # Составляем команду для запуска
    command = ['./tg_history_dumper', '-config', config_path]
    
    # Запускаем процесс
    process = Popen(command, stdout=PIPE, stderr=PIPE, text=True, bufsize=1)
    
    # Логируем вывод процесса
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            logger.info(f'STDOUT: {output.strip()}')
        err = process.stderr.readline()
        if err:
            logger.error(f'STDERR: {err.strip()}')

    process.wait()

@app.route('/run_dumper', methods=['POST'])
def run_dumper():
    data = request.json
    api_id = data['api_id']
    api_hash = data['api_hash']
    
    # Запускаем процесс в фоновом режиме
    thread = threading.Thread(target=run_process_and_log, args=(api_id, api_hash))
    thread.start()
    
    return jsonify({"success": True, "message": "Process started"}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001)
