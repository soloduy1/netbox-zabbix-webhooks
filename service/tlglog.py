import telebot
import os
from dotenv import load_dotenv


load_dotenv()
token = os.getenv('TG_TOKEN')
chatId = os.getenv('TG_CHATID')

bot = telebot.TeleBot(token)


def send_tg(msg):
    bot.send_message(chatId, text=msg)
