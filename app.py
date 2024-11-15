import telebot
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from dotenv import load_dotenv
import os

load_dotenv()

IS_DEV = True
IS_DEV = False # <--- comment that string for dev mode, do not commit

BOT_TOKEN = os.getenv('BOT_TOKEN_DEV' if IS_DEV else 'BOT_TOKEN')
API_KEY = os.getenv('API_KEY')
PASS = os.getenv('PASS')

bot = telebot.TeleBot(BOT_TOKEN)
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")
authorized = set()
waiting_for_pass = set()
chats = dict()
safety={
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE
}


@bot.message_handler(commands=['start', 'hello'])
def command_start_handler(message):
    bot.reply_to(message, 'Среда?\n/auth для входа')


@bot.message_handler(commands=['auth'])
def command_auth_handler(message):
    uid = message.from_user.id
    if authorized.__contains__(uid):
        bot.reply_to(message, 'Уже квакаем, все ок!')
    elif waiting_for_pass.__contains__(uid):
        bot.reply_to(message, 'Квакни пароль')
    else:
        bot.reply_to(message, 'Квакни пароль')
        waiting_for_pass.add(uid)


@bot.message_handler(commands=['reset'])
def command_reset_chat_handler(message):
    uid = message.from_user.id
    if not chats.__contains__(uid):
        bot.reply_to(message, 'А мы и так не квакали')
    else:
        chats.pop(uid)
        bot.reply_to(message, 'Готово, больше не квакаем')


@bot.message_handler(func=lambda msg: True)
def message_receive_handler(message):
    uid = message.from_user.id
    if waiting_for_pass.__contains__(uid):
        if message.text == PASS:
            authorized.add(uid)
            waiting_for_pass.remove(uid)
            bot.reply_to(message, 'Среда чюваки!')
        else:
            bot.reply_to(message, 'Не среда, пароль неверный(')
        return

    if not authorized.__contains__(uid):
        bot.reply_to(message, 'Не среда.\n/auth для входа')
        return

    try:
        if not chats.__contains__(uid):
            chats[uid] = model.start_chat()
        c = chats[uid]
        res_message = bot.reply_to(message, 'Ща...')
        res_text = ''
        response = c.send_message(message.text, safety_settings=safety, stream=True)
        for chunk in response:
            res_text += chunk.text
            res_message = bot.edit_message_text(res_text, chat_id=res_message.chat.id, message_id=res_message.message_id)

    except Exception as e:
        bot.reply_to(message, 'Все квакнулось\n' + repr(e))


print('croak, starting polling...')
bot.infinity_polling()
