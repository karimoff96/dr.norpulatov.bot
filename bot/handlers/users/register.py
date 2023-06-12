from bot.models import Patient
from bot.loader import bot, logger
from telebot.types import Message

from bot.keyboards.default import make_default_keyboard, contact_share_button, menu_buttons, register_button


from django.utils.translation import gettext_lazy as _

# from telegram_bot.loader import bot, logger

@bot.message_handler(func=lambda x: x.text == str(_("Ro`yhatdan o`tish")))

def register(message):
    bot.send_message(
        chat_id=message.chat.id,
        text=str(_('send_your_full_name')),
        reply_markup=make_default_keyboard([message.from_user.first_name])
    )
    bot.register_next_step_handler(message, get_first_name)

def get_first_name(message: Message):
    bot_user = Patient.objects.get(user_id=message.from_user.id)

    bot_user.first_name = message.text
    bot.send_message(
        chat_id=message.chat.id,
        text=str(_('select_your_role')),
        reply_markup=make_default_keyboard(list(roles))
    )
    bot.register_next_step_handler(message, get_role)

    markup = types.ReplyKeyboardMarkup(
        row_width=1, resize_keyboard=True, one_time_keyboard=True
    )
    btn = types.KeyboardButton(message.from_user.first_name)
    bot_user.step = 1
    bot_user.save()
    markup.add(btn)
    bot.send_message(
        message.from_user.id, str(_("Ismingizni kiriting!")), reply_markup=markup
    )