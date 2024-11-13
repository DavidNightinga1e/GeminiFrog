import telebot
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
API_KEY = os.getenv('API_KEY')
PASS = os.getenv('PASS')

bot = telebot.TeleBot(BOT_TOKEN)
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")
whitelisted = set()
chats = dict()
safety={
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE
}

@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message, 'Среда?\n/auth <пароль> для входа')

@bot.message_handler(commands=['reset'])
def reset_chat(message):
    uid = message.from_user.id
    if not chats.__contains__(uid):
        bot.reply_to(message, 'А мы и так не квакали')
    else:
        chats.pop(uid)
        bot.reply_to(message, 'Готово, больше не квакаем')

@bot.message_handler(commands=['auth'])
def auth(message):
    if message.text == PASS:
        whitelisted.add(message.from_user.id)
        bot.reply_to(message, 'Среда чюваки!')
    else:
        bot.reply_to(message, 'Не среда(')

@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    uid = message.from_user.id
    if not whitelisted.__contains__(uid):
        bot.reply_to(message, 'Не среда.\n/auth <пароль> для входа')
        return

    try:
        if not chats.__contains__(uid):
            chats[uid] = model.start_chat()
        c = chats[uid]
        response = c.send_message(message.text, safety_settings=safety)
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, 'Все квакнулось\n' + repr(e))

bot.infinity_polling()
