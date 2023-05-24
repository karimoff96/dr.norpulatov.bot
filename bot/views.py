from django.shortcuts import render
from telebot import types
import telebot
from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Patient, Doctor

# Create your views here.


bot = telebot.TeleBot(
    "5766441546:AAH8XwImaQhBngpA4xutYpm_MFI6ZjLkidE", parse_mode="HTML"
)

hideBoard = types.ReplyKeyboardRemove()


@csrf_exempt
def index(request):
    if request.method == "GET":
        return HttpResponse("<a href='http://t.me/dkarimoff96'>Created by</>")
    if request.method == "POST":
        bot.process_new_updates(
            [telebot.types.Update.de_json(request.body.decode("utf-8"))]
        )
        return HttpResponse(status=200)


@bot.message_handler(commands=["start"])
def start(message):
    # if Patient.objects.filter(user_id=message.from_user.id).exists():
    #     text = 'Shifokor qabuliga yozilish'

    # else:
    text = f"<i>Assalomu alaykum {message.from_user.first_name}.\n<b>shifokor qabuliga yozilish!</b></i>"
    bot_user=Patient.objects.create(user_id=message.from_user.id)
    bot_user.save()
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn = types.KeyboardButton("Qabulga yozilish")
    btn1 = types.KeyboardButton("Yordam")
    markup.add(btn, btn1)
    bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot_user = Patient.objects.get(user_id=message.from_user.id)
    if message.text == "Qabulga yozilish":
        print(121321)
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        btn1 = types.KeyboardButton("🛑Bekor qilish")
        markup.add(btn1)
        bot_user.username = message.from_user.username
        bot_user.save()
        msg = bot.reply_to(message, "Enter your first name", reply_markup=markup)
        bot.register_next_step_handler(msg, first_name_step)

    elif message.text == "🛑Bekor qilish":
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        btn = types.KeyboardButton("Qabulga yozilish")
        btn1 = types.KeyboardButton("Yordam")
        markup.add(btn1, btn)
        bot.send_message(
            message.chat.id, "<b>Shifokor qabuliga yozilish</b>", reply_markup=markup
        )


def first_name_step(message):
    bot_user = Patient.objects.get(user_id=message.from_user.id)

    try:
        bot_user.first_name = message.text
        bot_user.save()
        msg = bot.reply_to(message, "Enter your last name")
        bot.register_next_step_handler(msg, last_name_step)
    except Exception as e:
        bot.reply_to(message, "oooops")


def last_name_step(message):
    bot_user = Patient.objects.get(user_id=message.from_user.id)

    try:
        bot_user.last_name = message.text
        bot_user.save()
        msg = bot.reply_to(message, "What is the complain")
        bot.register_next_step_handler(msg, complain_step)
    except Exception as e:
        bot.reply_to(message, "oooops")


def complain_step(message):
    bot_user = Patient.objects.get(user_id=message.from_user.id)
    bot_user.reason = message.text
    bot_user.active = True
    bot_user.save()
    bot.send_message(
        message, "We have succesfully registered you in doctor's appointment"
    )
