
from telebot import types
from django.utils.translation import gettext_lazy as _


def main():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn = types.KeyboardButton(str(_("Qabulga yozilish")))
    btn1 = types.KeyboardButton(str(_("Tezkor Aloqa")))
    btn2 = types.KeyboardButton(str(_("Profil")))
    markup.add(btn, btn1, btn2)
    return markup