import os
import shutil
import zipfile
import logging
import asyncio
import random
import string
import aiohttp
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# Токен бота
TOKEN = '1234567890987654321'

# Логирование
logging.basicConfig(level=logging.INFO, filename="bot.log", filemode="a")
logger = logging.getLogger(__name__)

CHANNEL_ID = "@xtremebyte"

# ID администратора
ADMIN_ID = 123456789

def generate_prefix():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=4))

# Проверка подписки
async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user_id = update.effective_user.id
    try:
        chat_member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        if chat_member.status in ["member", "creator", "administrator"]:
            return True
    except Exception:
        pass
    keyboard = [[InlineKeyboardButton("Подписаться", url=f"https://t.me/{CHANNEL_ID[1:]}")]]
    await update.message.reply_text("⚠️ Подпишитесь на канал перед использованием бота.", reply_markup=InlineKeyboardMarkup(keyboard))
    return False

def subscription_required(handler_func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if await check_subscription(update, context):
            await handler_func(update, context)
    return wrapper

#start
@subscription_required
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я конвертирую BTX-файлы в PNG. Отправь ZIP, одиночный BTX или ссылку на файл!")

#info
@subscription_required
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Этот бот принимает ZIP-архивы, одиночные BTX-файлы или ссылки на них, конвертирует в PNG.")

#agreement
@subscription_required
async def agreement(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⚠️ Используя этот бот, вы соглашаетесь, что автор не несёт ответственности за его использование.")

#feedback
@subscription_required
async def feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.replace("/feedback", "").strip()
    user_id = update.effective_user.id
    if not text:
        await update.message.reply_text("Напишите отзыв после команды, например: /feedback Бот супер!")
        return
    await update.message.reply_text("Спасибо за отзыв! Он отправлен разработчику.")
    await context.bot.send_message(chat_id=ADMIN_ID, text=f"Обратная связь от {user_id}: {text}")

#help
@subscription_required
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📋 **Справка по боту**\n\n"
        "Я конвертирую BTX-файлы в PNG. Вот как со мной работать:\n\n"
        "1️⃣ **Отправь файл BTX:** Просто загрузите файл .btx — я верну PNG.\n"
        "   Пример: file.btx\n\n"
        "2️⃣ **Отправь ZIP-архив:** Загрузите .zip с BTX-файлами — получите ZIP с PNG.\n"
        "   Пример: archive.zip (до 50 МБ)\n\n"
        "3️⃣ **Отправь ссылку:** Кидайте ссылку на .btx или .zip (например, с Google Drive).\n"
        "   Пример: https://drive.google.com/file/d/12345/view\n\n"
        "4️⃣ **Команды:**\n"
        "   /start — Запустить бота\n"
        "   /info — Узнать, что я умею\n"
        "   /agreement — Пользовательское соглашение\n"
        "   /feedback [текст] — Отправить отзыв разработчику\n"
        "   /help — Показать эту справку\n\n"
        "💡 Подпишитесь на @xtremebyte, чтобы начать работу!\n"
        "Если что-то не получается, пишите через /feedback."
    )
    await update.message.reply_text(help_text)


async def process_btx_file(file_path, user_dir):
    if not os.path.isfile(file_path):
        return False
    with open(file_path, 'rb+') as file:
        file.seek(4)
        data = file.read()
    file_name = os.path.splitext(os.path.basename(file_path))[0]
    ktx_file_path = os.path.join(user_dir, f"{file_name}.ktx")
    with open(ktx_file_path, 'wb') as ktx_file:
        ktx_file.write(data)

    process = await asyncio.create_subprocess_exec("convertXtremeByte.exe", "-d", "-i", ktx_file_path,
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    await process.communicate()

    png_files = []
    for file_name in os.listdir(user_dir):
        if file_name.endswith("_Out.png"):
            new_file_name = file_name.replace("_Out", "")
            os.rename(os.path.join(user_dir, file_name), os.path.join(user_dir, new_file_name))
            png_files.append(new_file_name)
    return png_files if png_files else False


@subscription_required
async def handle_btx_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        document = update.message.document
        if not document.file_name.endswith('.btx'):
            await update.message.reply_text("Ошибка: Отправьте файл с расширением .btx!")
            return

        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        user_dir = f"user_{user_id}"
        os.makedirs(user_dir, exist_ok=True)

        file_obj = await document.get_file()
        btx_file_path = os.path.join(user_dir, document.file_name)
        await file_obj.download_to_drive(btx_file_path)

        await update.message.reply_text("Обработка BTX началась...")

        png_files = await process_btx_file(btx_file_path, user_dir)
        if not png_files:
            await update.message.reply_text("Ошибка: Не удалось сконвертировать файл.")
            shutil.rmtree(user_dir, ignore_errors=True)
            return

        for png_file in png_files:
            with open(os.path.join(user_dir, png_file), 'rb') as png:
                await context.bot.send_document(chat_id=chat_id, document=png, caption=f"Ваш файл: {png_file}")

        shutil.rmtree(user_dir, ignore_errors=True)

    except Exception as e:
        await update.message.reply_text("Ошибка при обработке файла.")
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"Ошибка у пользователя {user_id} при обработке BTX: {str(e)}")


@subscription_required
async def handle_zip_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        document = update.message.document
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id

        if document.file_size > 50 * 1024 * 1024:
            await update.message.reply_text("Ошибка: Максимальный размер ZIP — 50 MB.")
            return

        file_obj = await document.get_file()
        user_dir = f"user_{user_id}"
        os.makedirs(user_dir, exist_ok=True)
        zip_file_path = os.path.join(user_dir, document.file_name)
        await file_obj.download_to_drive(zip_file_path)

        try:
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                zip_ref.extractall(user_dir)
        except Exception:
            await update.message.reply_text("Ошибка: Не удалось распаковать ZIP-архив.")
            shutil.rmtree(user_dir, ignore_errors=True)
            return

        btx_files = [os.path.join(root, f) for root, _, files in os.walk(user_dir) for f in files if f.endswith('.btx')]
        if not btx_files:
            await update.message.reply_text("BTX-файлы не найдены.")
            shutil.rmtree(user_dir, ignore_errors=True)
            return

        await update.message.reply_text("Обработка файлов началась...")

        all_png_files = []
        for btx_file in btx_files:
            png_files = await process_btx_file(btx_file, user_dir)
            if png_files:
                all_png_files.extend(png_files)

        if not all_png_files:
            await update.message.reply_text("Ошибка конвертации файлов.")
            shutil.rmtree(user_dir, ignore_errors=True)
            return

        original_name = os.path.splitext(document.file_name)[0]
        prefix = generate_prefix()
        final_zip_name = f"{prefix}_{original_name}.zip"
        final_zip_path = os.path.join(user_dir, final_zip_name)

        with zipfile.ZipFile(final_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for png_file in all_png_files:
                zipf.write(os.path.join(user_dir, png_file), arcname=png_file)

        with open(final_zip_path, 'rb') as zipf:
            await context.bot.send_document(chat_id=chat_id, document=zipf, caption=f"Ваш архив: {final_zip_name}")

        shutil.rmtree(user_dir, ignore_errors=True)

    except Exception as e:
        await update.message.reply_text("Ошибка при обработке архива.")
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"Ошибка у пользователя {user_id} при обработке ZIP: {str(e)}")


@subscription_required
async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        url = update.message.text.strip()
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id

        if not re.match(r'^https?://', url):
            await update.message.reply_text("Ошибка: Отправьте действительную ссылку (http/https).")
            return

        if "drive.google.com" in url:
            match = re.search(r'/d/([a-zA-Z0-9_-]+)', url)
            if match:
                file_id = match.group(1)
                url = f"https://drive.google.com/uc?export=download&id={file_id}"
            else:
                await update.message.reply_text("Ошибка: Неверный формат ссылки Google Drive.")
                return

        await update.message.reply_text("Скачиваю файл по ссылке...")

        user_dir = f"user_{user_id}"
        os.makedirs(user_dir, exist_ok=True)

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    await update.message.reply_text("Ошибка: Не удалось скачать файл.")
                    shutil.rmtree(user_dir, ignore_errors=True)
                    return

                content_disposition = resp.headers.get('Content-Disposition')
                if content_disposition and 'filename=' in content_disposition:
                    file_name = content_disposition.split('filename=')[-1].strip('";')
                else:
                    content_type = resp.headers.get('Content-Type', '').lower()
                    prefix = generate_prefix()
                    if 'zip' in content_type:
                        file_name = f"downloaded_{prefix}.zip"
                    elif 'octet-stream' in content_type:
                        file_name = f"downloaded_{prefix}.btx"
                    else:
                        file_name = f"downloaded_{prefix}.bin"

                file_path = os.path.join(user_dir, file_name)

                with open(file_path, 'wb') as f:
                    f.write(await resp.read())

        if file_name.endswith('.btx'):
            await update.message.reply_text("Обработка BTX началась...")
            png_files = await process_btx_file(file_path, user_dir)
            if not png_files:
                await update.message.reply_text("Ошибка: Не удалось сконвертировать файл.")
                shutil.rmtree(user_dir, ignore_errors=True)
                return
            for png_file in png_files:
                with open(os.path.join(user_dir, png_file), 'rb') as png:
                    await context.bot.send_document(chat_id=chat_id, document=png, caption=f"Ваш файл: {png_file}")

        elif file_name.endswith('.zip'):
            try:
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(user_dir)
            except Exception:
                await update.message.reply_text("Ошибка: Не удалось распаковать ZIP.")
                shutil.rmtree(user_dir, ignore_errors=True)
                return

            btx_files = [os.path.join(root, f) for root, _, files in os.walk(user_dir) for f in files if f.endswith('.btx')]
            if not btx_files:
                await update.message.reply_text("BTX-файлы не найдены.")
                shutil.rmtree(user_dir, ignore_errors=True)
                return

            await update.message.reply_text("Обработка файлов началась...")
            all_png_files = []
            for btx_file in btx_files:
                png_files = await process_btx_file(btx_file, user_dir)
                if png_files:
                    all_png_files.extend(png_files)

            if not all_png_files:
                await update.message.reply_text("Ошибка конвертации файлов.")
                shutil.rmtree(user_dir, ignore_errors=True)
                return

            prefix = generate_prefix()
            final_zip_name = f"{prefix}_downloaded.zip"
            final_zip_path = os.path.join(user_dir, final_zip_name)
            with zipfile.ZipFile(final_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for png_file in all_png_files:
                    zipf.write(os.path.join(user_dir, png_file), arcname=png_file)

            with open(final_zip_path, 'rb') as zipf:
                await context.bot.send_document(chat_id=chat_id, document=zipf, caption=f"Ваш архив: {final_zip_name}")

        else:
            await update.message.reply_text("Ошибка: Не удалось определить тип файла. Убедитесь, что ссылка ведёт на .btx или .zip.")

        shutil.rmtree(user_dir, ignore_errors=True)

    except Exception as e:
        await update.message.reply_text("Ошибка при обработке ссылки.")
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"Ошибка у пользователя {user_id} при обработке ссылки: {str(e)}")


async def set_bot_commands(application):
    commands = [
        BotCommand("start", "Запуск бота"),
        BotCommand("info", "Как работает бот"),
        BotCommand("agreement", "Пользовательское соглашение"),
        BotCommand("feedback", "Отправить отзыв разработчику"),
        BotCommand("help", "Показать справку по боту"), 
    ]
    await application.bot.set_my_commands(commands)


def main():
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("info", info))
    application.add_handler(CommandHandler("agreement", agreement))
    application.add_handler(CommandHandler("feedback", feedback))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.Document.MimeType('application/zip'), handle_zip_file))
    application.add_handler(MessageHandler(filters.Document.FileExtension('btx'), handle_btx_file))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))
    application.post_init = set_bot_commands
    application.run_polling()

if __name__ == '__main__':
    main()