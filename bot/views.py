from django.shortcuts import render
from telebot import types
import telebot
from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Patient, Doctor
from django.utils.translation import gettext_lazy as _
from environs import Env

# Create your views here.
env = Env()
env.read_env()

CHANNEL = env.str("CHANNEL")
bot = telebot.TeleBot(env.str("BOT_TOKEN"), parse_mode="HTML")


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
    if Patient.objects.filter(user_id=message.from_user.id).exists():
        bot_user = Patient.objects.get(user_id=message.from_user.id)
        bot_user.step = 0
        bot_user.save()
        text = str(_("Shifokor qabuliga yozilish"))

    else:
        Patient.objects.create(
            user_id=message.from_user.id, first_name=message.from_user.first_name
        )
        text = str(
            _(
                f"<i>Assalomu alaykum {message.from_user.first_name}.\n<b>shifokor qabuliga yozilish!</b></i>"
            )
        )

    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn = types.KeyboardButton(str(_("Qabulga yozilish")))
    btn1 = types.KeyboardButton(str(_("Tezkor Aloqa")))
    markup.add(btn, btn1)
    bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == str(_("🛑Bekor qilish")))
def cancel(message):
    user = Patient.objects.get(user_id=message.from_user.id)
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn = types.KeyboardButton(str(_("Qabulga yozilish")))
    btn1 = types.KeyboardButton(str(_("Tezkor Aloqa")))
    markup.add(btn, btn1)
    user.urgent=False
    user.step = 0
    user.save()
    bot.send_message(
        message.chat.id,
        str(_("<b>Shifokor qabuliga yozilish</b>")),
        reply_markup=markup,
    )


@bot.message_handler(func=lambda message: message.text == str(_("Qabulni ko`rish")))
def checkout(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn = types.KeyboardButton(str(_("Qabulga yozilish")))
    btn1 = types.KeyboardButton(str(_("Qabulni ko`rish")))
    btn2 = types.KeyboardButton(str(_("Tezkor Aloqa")))
    markup.add(btn, btn1, btn2)
    user = Patient.objects.get(user_id=message.from_user.id)
    if user.urgent == True:
        print(1213121)
        if len(message.from_user.username) > 0:
            text = f"<u><b>‼️Tezkor qabul.\nFoydalanuvchi ma`lumotlari:</b></u>\n<b>Tartib raqami:</b>  {user.id}\n<b>Ismi:</b>  {user.first_name}\n<b>Profil:</b>  {user.username}\n<b>Telefon raqam:</b>  {user.phone_number}"
        else:
            text = f"<u><b>‼️Tezkor qabul.\nFoydalanuvchi ma`lumotlari:</b></u>\n<b>Tartib raqami:</b>  {user.id}\n<b>Ismi:</b>  {user.first_name}\n<b>Telefon raqam:</b>  {user.phone_number}"
    else:
        if len(message.from_user.username) > 0:
            text = str(
                _(
                    f"<u><b>Foydalanuvchi ma`lumotlari:</b></u>\n<b>Tartib raqami:</b>  {user.id}\n<b>Ismi:</b>  {user.first_name}\n<b>Familyasi:</b>  {user.last_name}\n<b>Profil:</b>  {user.username}\n<b>Telefon raqam:</b> {user.phone_number}\n<b>Shikoyat bayoni:</b>  {user.reason}\n"
                )
            )
        else:
            text = str(
                _(
                    f"<u><b>Foydalanuvchi ma`lumotlari:</b></u>\n<b>Tartib raqami:</b>  {user.id}\n<b>Ismi:</b>  {user.first_name}\n<b>Familyasi:</b>  {user.last_name}\n<b>Telefon raqam:</b> {user.phone_number}\n<b>Shikoyat bayoni:</b>  {user.reason}\n"
                )
            )

    bot.send_message(message.from_user.id, text, reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == str(_("Qabulga yozilish")))
def register(message):
    bot_user = Patient.objects.get(user_id=message.from_user.id)
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton(str(_("🛑Bekor qilish")))
    markup.add(btn1)
    bot_user.username = message.from_user.username
    bot_user.step = 1
    bot_user.urgent=False
    bot_user.save()
    bot.send_message(
        message.chat.id, str(_("Ismingizni kiriting:")), reply_markup=markup
    )

@bot.message_handler(func=lambda message: message.text == str(_("Tezkor Aloqa")))
def first_aid(message):
    text = """Agar sizda  bosh og'rig'i, qusish, isitma yoki ko’krak og’riqlari paydo bo'lsa, darhol tibbiy yordam talab qilinishi mumkin.\nQuyidagi belgilar sizda mavjud bo’lsa, tezkor yordam tugmasini bosing.\n\n📌Qattiq bo'yin yoki iyak og'rig'i.\n📌Chalkashish, fikrlarni o’chib ketishi\n📌Haddan tashqari uyquchanlik.\n📌Yurakning tez urishi yoki yurak atrofidagi noqulayliklar.\n📌Doimiy ko'ngil aynishi yoki qayt qilish.\n📌Nurga kuchli sezgirlik (fotofobiya).\n📌Tik turish yoki yurishga xalaqit beradigan beqarorlik (ataksiya yoki vertigo).\n📌Yangi ikki tomonlama ko'rish, loyqa ko'rish yoki ko'r dog'lar.\n📌Juda tez, qiyin nafas olish.\n📌Yangi va turli xil teri toshmasi yoki kuchli ko'karishlar.\n📌Bir yoki bir nechta bo'g'imlarda yangi shish, og'riq, qizarish yoki issiqlik.\n\nBizning hizmatlar faqat diagnos qoyish va konsultatsiya berishdan iborat. Agar sizga tezkor yordam kerak bo’lsa 103 ga qo’ng’iroq qiling."""
    bot.send_message(message.from_user.id, text)
    bot_user = Patient.objects.get(user_id=message.from_user.id)
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton(str(_("🛑Bekor qilish")))
    markup.add(btn1)
    bot_user.username = message.from_user.username
    bot_user.step = 100
    bot_user.urgent = True
    bot_user.save()
    bot.send_message(
        message.chat.id, str(_("Ismingizni kiriting:")), reply_markup=markup
    )
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot_user = Patient.objects.get(user_id=message.from_user.id)
    if len(message.text) > 0 and bot_user.step == 1:
        bot_user.first_name = message.text
        bot_user.step = 2
        bot_user.save()
        bot.send_message(message.chat.id, str(_("Familyangizni kiriting:")))

    elif len(message.text) > 0 and bot_user.step == 2:
        bot_user.last_name = message.text
        bot_user.step = 3
        bot_user.save()
        bot.send_message(
            message.chat.id, str(_("Shikoyatingiz haqida batafsil ma`lumot bering:"))
        )

    elif len(message.text) > 0 and bot_user.step == 3:
        bot_user.reason = message.text
        bot_user.save()
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add(
            types.KeyboardButton(
                str(_("Telefon raqamni ulashish")), request_contact=True
            )
        )
        bot.send_message(
            message.chat.id,
            str(_("Telefon raqamingizni kiriting:")),
            reply_markup=markup,
        )

    elif len(message.text) > 0 and bot_user.step == 100 and bot_user.urgent == True:
        bot_user.first_name = message.text
        bot_user.step = 101
        bot_user.save()
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add(
            types.KeyboardButton(
                str(_("Telefon raqamni ulashish")), request_contact=True
            )
        )
        bot.send_message(
            message.chat.id,
            str(_("Telefon raqamingizni kiriting:")),
            reply_markup=markup,
        )


@bot.message_handler(content_types=["contact"])
def contact(message):
    user = Patient.objects.get(user_id=message.from_user.id)
    if message.contact is not None and message.contact.phone_number:
        phone_number = message.contact.phone_number
        user.phone_number = phone_number
        user.active = True
        user.step = 0

        user.save()
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        btn = types.KeyboardButton(str(_("Qabulga yozilish")))
        btn1 = types.KeyboardButton(str(_("Qabulni ko`rish")))
        btn2 = types.KeyboardButton(str(_("Tezkor Aloqa")))
        markup.add(btn, btn1, btn2)
        bot.send_message(
            message.chat.id, str(_(f"Telefon raqam qabul qilindi: {phone_number}"))
        )
        bot.send_message(
            message.from_user.id,
            str(_("Shifokor qabuliga yozilish muvaffaqiyatli yakunlandi! ")),
            reply_markup=markup,
        )
        if user.urgent == True:
            if len(message.from_user.username) > 0:
                text = f"<u><b>‼️Tezkor qabul.\nFoydalanuvchi ma`lumotlari:</b></u>\n<b>Tartib raqami:</b>  {user.id}\n<b>Ismi:</b>  {user.first_name}\n<b>Profil:</b>  {user.username}\n<b>Telefon raqam:</b>  {user.phone_number}"
            else:
                text = f"<u><b>‼️Tezkor qabul.\nFoydalanuvchi ma`lumotlari:</b></u>\n<b>Tartib raqami:</b>  {user.id}\n<b>Ismi:</b>  {user.first_name}\n<b>Telefon raqam:</b>  {user.phone_number}"
            user.step=0
            # user.urgent=False
            user.save()
            bot.send_message(message.from_user.id, 'Siz bilan tez orada bog`lanishadi!')

        else:
            if len(message.from_user.username) > 0:
                text = str(
                    _(
                        f"<u><b>Foydalanuvchi ma`lumotlari:</b></u>\n<b>Tartib raqami:</b>  {user.id}\n<b>Ismi:</b>  {user.first_name}\n<b>Familyasi:</b>  {user.last_name}\n<b>Profil:</b>  {user.username}\n<b>Telefon raqam:</b> {user.phone_number}\n<b>Shikoyat bayoni:</b>  {user.reason}\n"
                    )
                )
            else:
                text = str(
                    _(
                        f"<u><b>Foydalanuvchi ma`lumotlari:</b></u>\n<b>Tartib raqami:</b>  {user.id}\n<b>Ismi:</b>  {user.first_name}\n<b>Familyasi:</b>  {user.last_name}\n<b>Telefon raqam:</b> {user.phone_number}\n<b>Shikoyat bayoni:</b>  {user.reason}\n"
                    )
                )
        # bot.send_message(CHANNEL, text)


