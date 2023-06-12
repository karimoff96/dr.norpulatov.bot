import telebot

from django.conf import settings

logger = telebot.logger
bot = telebot.TeleBot(settings.BOT_TOKEN, parse_mode='HTML')
