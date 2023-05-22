from django.shortcuts import render
from telebot import types
import telebot
from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Patient, Doctor

# Create your views here.


bot = telebot.TeleBot('5916180901:AAEMs2myndk2LH_vTyuxmB1euuYgSGJtdHU', parse_mode="HTML")

hideBoard = types.ReplyKeyboardRemove()


@csrf_exempt
def index(request):
    if request.method == 'GET':
        return HttpResponse("<a href='http://t.me/dkarimoff96'>Created by</>")
    if request.method == 'POST':
        bot.process_new_updates([
            telebot.types.Update.de_json(
                request.body.decode("utf-8")
            )
        ])
        return HttpResponse(status=200)


@bot.message_handler(commands=["start"])
def start(message):
    if Patient.objects.filter(user_id=message.from_user.id).exists():
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        btn = types.KeyboardButton('Qabulga yozilish')
        btn1 = types.KeyboardButton('Yordam')
        markup.add(btn1, btn)
        bot.send_message(message.chat.id, "<b>Shifokor qabuliga yozilish</b>", reply_markup=markup)
        bot_user = Patient.objects.get(user_id=message.from_user.id)

    else:
        text = f'<i>Assalomu alaykum {message.from_user.first_name}.\n<b>shifokor qabuliga yozilish!</b></i>'
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        btn = types.KeyboardButton('Qabulga yozilish')
        btn1 = types.KeyboardButton('Yordam')
        markup.add(btn1, btn)
        bot.send_message(message.chat.id, text, reply_markup=markup)
        bot_user = Patient.objects.create(user_id=message.from_user.id, username=message.from_user.username)
        bot_user.save()


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot_user = Patient.objects.get(user_id=message.from_user.id)
    if message.text == '🚘Avtomobil':
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        btn1 = types.KeyboardButton('🛑Bekor qilish')
        markup.add(btn1)
        bot.register_next_step_handler(msg, process_name_step)
        bot.send_message(message.chat.id, , reply_markup=markup)
        bot.send_message(message.chat.id, "<b>👤Ismingizni kiriting</b>")