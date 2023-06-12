from django.utils.translation import gettext_lazy as _
from telebot.types import Message
from telebot import types

from bot.loader import bot
# from bot.keyboards.default import menu_buttons, register_button

from bot.models import Patient, Doctor

@bot.message_handler(commands=["start"])
def start(message):
    if len(message.text.split()) > 1:
        doc = Doctor.objects.filter(doc_token=message.text.split()[1]).first()
        doc.doc_id = message.from_user.id
        doc.active = True
        doc.save()
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        btn = types.KeyboardButton(str(_("Mening qabulim")))
        # btn1 = types.KeyboardButton(str(_("Tezkor Aloqa")))
        markup.add(btn)
        bot.send_message(
            message.from_user.id,
            f"Assalomu alaykum doktor {doc.first_name}!\nBu bot sizning mavjud va yangi qabulingizga yozilgan be`morlar haqida ma`lumot beradi",
            reply_markup=markup,
        )
    else:
        user = Patient.objects.filter(user_id=message.from_user.id).first()
        doc = Doctor.objects.filter(doc_id=message.from_user.id).first()
        if user:
            if user.active == True:
                markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
                btn = types.KeyboardButton(str(_("Qabulga yozilish")))
                btn1 = types.KeyboardButton(str(_("Tezkor Aloqa")))
                markup.add(btn, btn1)
                bot.send_message(
                    message.chat.id,
                    str(_("<b>Shifokor qabuliga yozilish</b>")),
                    reply_markup=markup,
                )
            else:
                user.first_name=message.from_user.first_name
                user.username=message.from_user.username if message.from_user.username else ''
                user.first_name=message.from_user.first_name
                user.source="bot"
                user.save()
                text = "Tinlni tanlang\nТинлни танланг"
                markup = types.InlineKeyboardMarkup(row_width=2)
                b = types.InlineKeyboardButton("Lotin", callback_data="en")
                b1 = types.InlineKeyboardButton("Кирилл", callback_data="ru")
                markup.add(b, b1)
                bot.send_message(message.chat.id, text, reply_markup=markup)

        elif doc:
            markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
            btn = types.KeyboardButton(str(_("Mening qabulim")))
            # btn1 = types.KeyboardButton(str(_("Tezkor Aloqa")))
            markup.add(btn)
            bot.send_message(
                message.from_user.id,
                f"Assalomu alaykum doktor {doc.first_name}!",
                reply_markup=markup,
            )
        else:
            Patient.objects.create(
                user_id=message.from_user.id,
                username=message.from_user.username if message.from_user.username else '',
                first_name=message.from_user.first_name,
                source="bot",
            )
            text = "Tinlni tanlang\nТинлни танланг"
            markup = types.InlineKeyboardMarkup(row_width=2)
            b = types.InlineKeyboardButton("Lotin", callback_data="en")
            b1 = types.InlineKeyboardButton("Кирилл", callback_data="ru")
            markup.add(b, b1)
            bot.send_message(message.chat.id, text, reply_markup=markup)