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

## Консольная утилита

Консольная утилита `util.py` предназначена для взаимодействия с Telegram History Dumper и управления архивацией переписок. Утилита поддерживает следующие ключи командной строки:

- `--update`: запускает процесс обновления данных.
- `--api_id`: ваш API ID от Telegram.
- `--api_hash`: ваш API Hash от Telegram.
- `--phone_number`: номер телефона, ассоциированный с аккаунтом Telegram.

### Использование

Для запуска утилиты используйте команду:
```bash
docker exec -it [container_id] python3 util.py --api_id ваш_ID --api_hash ваш_hash --phone_number ваш_номер
```
Замените `[container_id]` на идентификатор контейнера с веб-сервисом. Введите требуемые параметры `api_id`, `api_hash` и `phone_number` для доступа к функциям Telegram API.

### Пример
Для запуска утилиты и обновления данных:
```bash
docker exec -it [container_id] python3 util.py --update --api_id 12345 --api_hash abcdef123456 --phone_number +1234567890
```
Эта команда инициирует процесс обновления данных, используя указанные параметры доступа к API Telegram.

Вот расширенное описание возможности браузинга переписок через консольную утилиту:

### Браузинг переписок через консольную утилиту

Консольная утилита также позволяет просматривать архивы переписок через терминал. Эта функциональность полезна для быстрого доступа к истории чатов без использования графического интерфейса.

#### Использование
Для активации режима браузинга выполните команду:
```bash
docker exec -it [container_id] python3 util.py
```
После запуска утилиты используйте клавиши вверх и вниз для навигации по списку чатов, и ENTER для выбора чата и просмотра его истории.

#### Взаимодействие
В режиме просмотра чата можно скроллить историю сообщений, используя клавиши вверх и вниз. Выход из режима просмотра осуществляется нажатием клавиши ESC.

Эта функция делает утилиту многофункциональным инструментом для управления и анализа данных из Telegram непосредственно из командной строки.

## Лицензия
Данные о лицензии указаны в файле [LICENSE.MD](LICENSE.MD)
