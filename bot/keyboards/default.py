from django.utils.translation import gettext_lazy as _
from telebot.types import KeyboardButton, ReplyKeyboardMarkup


def make_default_keyboard(buttons: list, row_width: int = 2) -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=row_width)
    for button in buttons:
        keyboard.add(KeyboardButton(str(button)))
    return keyboard

menu_buttons = make_default_keyboard([_('Qabulga yozilish'), _('Tezkor Aloqa')])

register_button = make_default_keyboard([_('register')])

contact_share_button = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=True)
contact_share_button.add(KeyboardButton(str(_('share_contact')), request_contact=True))