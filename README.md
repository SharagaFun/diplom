# Архиватор переписок из Telegram

## Описание
Это приложение предназначено для архивации и локального хранения переписок из мессенджера Telegram, используя микросервисную архитектуру и Docker.

## Компоненты системы

- **[Local Web Service (Flask, Frontend)](https://github.com/SharagaFun/diplom/web)**: Фронтенд сервис для управления архивацией.
- **Nginx (External Hosting, Port 80)**: Сервис для хостинга статических HTML-файлов, доступных через интернет.
- **[Telegram History Dumper](https://github.com/3bl3gamer/tg_history_dumper)**: Сервис для извлечения и архивации данных из Telegram.
- **[Ollama Service](https://github.com/ollama/ollama)**: Сервис для анализа и суммаризации текстов.

## Запуск проекта
Убедитесь, что у вас установлены Docker и Docker Compose:
```bash
git clone https://github.com/SharagaFun/diplom
cd diplom
docker-compose up --build
```

## Лицензия
Данные о лицензии указаны в файле [LICENSE.MD](LICENSE.MD)
