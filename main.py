
import os
import telebot
import openai
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime

# 🔐 Ключи из переменных окружения
TG_TOKEN = os.getenv("TG_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
USER_ID = os.getenv("USER_ID")  # Твой Telegram ID

bot = telebot.TeleBot(TG_TOKEN)
openai.api_key = OPENAI_API_KEY

context = [
    {"role": "system", "content": "Ты — личный коуч Дина. Ты работаешь в духе Виктора Франкла: помогаешь найти смысл, поддерживаешь, говоришь по-человечески и с уважением. Отвечай кратко и по делу."}
]

# Утренние, дневные, вечерние напоминания
def send_morning_message():
    bot.send_message(USER_ID, "Доброе утро, Дин 🌅\n\n1. Как ты себя чувствуешь?\n2. Кто ты хочешь быть сегодня?\n3. Что ты сделаешь для своей миссии?")

def send_day_check():
    bot.send_message(USER_ID, "Дин, как идёт день? ✅ Душ ✅ Медитация ✅ Завтрак ✅ Задача\nОтметь, что уже выполнил.")

def send_evening_reflection():
    bot.send_message(USER_ID, "🌙 Вечер.\n1. Что сегодня дало тебе смысл?\n2. Что было сложным?\n3. Чем ты гордишься?")

# Обработка /start и обычных сообщений
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет, Дин. Напиши, как ты себя чувствуешь.")

@bot.message_handler(func=lambda message: True)
def chat(message):
    context.append({"role": "user", "content": message.text})
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=context,
            temperature=0.8
        )
        reply = response.choices[0].message.content
        context.append({"role": "assistant", "content": reply})
        bot.send_message(message.chat.id, reply)
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {str(e)}")

# Планировщик задач
scheduler = BlockingScheduler()
scheduler.add_job(send_morning_message, 'cron', hour=6, minute=30)
scheduler.add_job(send_day_check, 'cron', hour=14, minute=0)
scheduler.add_job(send_evening_reflection, 'cron', hour=21, minute=30)

def run():
    from threading import Thread
    Thread(target=scheduler.start).start()
    bot.polling()

if __name__ == '__main__':
    run()
