Исходный код бота "xtreme bot"

🔥 Что умеет бот:

1. Конвертация BTX в PNG
Кидаешь файл .btx — получаешь готовый .png.

2. Обработка ZIP-архивов
Загружаешь .zip с BTX-файлами (до 50 МБ), бот распаковывает, конвертирует и возвращает архив с PNG.

3. Работа со ссылками
Отправляешь ссылку на .btx или .zip (например, с Google Drive), бот скачивает и делает всё сам.

4. Проверка подписки
Доступ только для подписчиков канала (можно настроить под свой канал).

Команды
/start — запуск бота
/info — что умеет бот
/agreement — соглашение
/feedback — отправить отзыв
/help — подробная справка

🛠 Как настроить бота:
Если хочешь запустить своего бота на основе этого кода, вот пошаговая инструкция:

1. Скачай код

2. Установи зависимости
Убедись, что у тебя есть Python 3.7+. Установи нужные библиотеки:

pip install python-telegram-bot aiohttp

3. Получи токен бота
Пиши @BotFather в Telegram, создай нового бота через /newbot и скопируй токен. Вставь его в код вместо TOKEN = '1234567890987654321'.

4. Настрой канал
Укажи ID своего канала в CHANNEL_ID = "@xtremebyte". Бот будет проверять подписку на него.
💡 ID канала — это @username (например, @xtremebyte).

5. Укажи ID админа
В ADMIN_ID = 123456789 впиши свой Telegram ID (узнать можно через @userinfobot). Сюда будут приходить ошибки и фидбек.

6. Добавь утилиту для конвертации
В коде используется convertNikeStudio.exe для обработки BTX-файлов. Убедись, что этот файл лежит рядом с convert.py.

7. Запусти бота

Если всё ок, бот стартанёт и будет ждать сообщений!

💡 Полезные советы:

Логи пишутся в bot.log — удобно для отладки.
Папки user_<id> создаются временно для каждого юзера и удаляются после обработки.
