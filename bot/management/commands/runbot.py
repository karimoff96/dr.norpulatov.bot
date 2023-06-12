import logging

from django.core.management.base import BaseCommand
from bot.loader import bot

from bot.handlers import *


class Command(BaseCommand):
    help = 'RUN COMMAND: python manage.py runbot'

    def handle(self, *args, **options):
        print('Bot is running...')
        bot.infinity_polling(logger_level=logging.DEBUG)
