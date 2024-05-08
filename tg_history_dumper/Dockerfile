# Используем официальный образ Go для компиляции
FROM golang:1.20 AS builder

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы модулей Go и локальные модули
COPY go.mod go.sum ./
COPY tgclient ./tgclient

# Загружаем зависимости
RUN go mod download

# Копируем остальной код приложения
COPY . .

# Собираем приложение
RUN CGO_ENABLED=0 go build -o tg_history_dumper

# Используем образ Python для выполнения
FROM python:3.12

# Устанавливаем requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исполняемый файл из билдера
WORKDIR /root/
COPY --from=builder /app/tg_history_dumper .

# Копируем скрипт Flask приложения
COPY dumper_service.py ./dumper_service.py

RUN mkdir -p /root/history/files

# Открываем порт, который будет использоваться Flask приложением
EXPOSE 5001

# Команда для запуска Flask приложения
CMD ["python3", "dumper_service.py"]
