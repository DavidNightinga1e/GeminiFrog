import telebot
import google.generativeai as genai
import os
import re
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from dotenv import load_dotenv


IS_DEV = True
IS_DEV = False # <--- comment that string for dev mode, do not commit

load_dotenv()

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
    bot.reply_to(message, localization['Welcome'])


@bot.message_handler(commands=['auth'])
def command_auth_handler(message):
    uid = message.from_user.id
    if authorized.__contains__(uid):
        bot.reply_to(message, localization['Auth_Already'])
    elif waiting_for_pass.__contains__(uid):
        bot.reply_to(message, localization['Auth_PasswordRequest'])
    else:
        bot.reply_to(message, localization['Auth_PasswordRequest'])
        waiting_for_pass.add(uid)


@bot.message_handler(commands=['reset'])
def command_reset_chat_handler(message):
    uid = message.from_user.id
    if not chats.__contains__(uid):
        bot.reply_to(message, localization['Context_Empty'])
    else:
        chats.pop(uid)
        bot.reply_to(message, localization['Context_Reset'])


@bot.message_handler(func=lambda msg: True)
def message_receive_handler(message):
    uid = message.from_user.id
    if waiting_for_pass.__contains__(uid):
        if message.text == PASS:
            authorized.add(uid)
            waiting_for_pass.remove(uid)
            bot.reply_to(message, localization['Auth_Success'])
        else:
            bot.reply_to(message, localization['Auth_WrongPassword'])
        return

    if not authorized.__contains__(uid):
        bot.reply_to(message, localization['Auth_NotAuthed'])
        return

    try:
        if not chats.__contains__(uid):
            chats[uid] = model.start_chat()
        c = chats[uid]
        res_message = bot.reply_to(message, localization['Gemini_Wait'])
        res_text = ''
        response = c.send_message(message.text, safety_settings=safety, stream=True)
        for chunk in response:
            res_text += chunk.text
            res_message = bot.edit_message_text(res_text, chat_id=res_message.chat.id, message_id=res_message.message_id)

    except Exception as e:
        bot.reply_to(message, localization['Gemini_Fail'] + '\n' + repr(e))


def load_localization():
    result_dict = {}
    with open('localization.txt', 'r', encoding='UTF-8') as f:
        file_content = f.read()
        pattern = r"'(.*?)'='(.*?)'"
        matches = re.findall(pattern, file_content)
        for key, value in matches:
            result_dict[key] = value.replace('\\n', '\n')
    return result_dict


print('reading localization file')
localization = load_localization()
print('croak, starting polling...')
bot.infinity_polling()
