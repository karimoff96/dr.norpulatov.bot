import datetime

import telebot
from django.shortcuts import HttpResponse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from environs import Env
from telebot import types
from telebot.apihelper import ApiTelegramException
from telebot.types import CallbackQuery

from telegram_bot_calendar import LSTEP, DetailedTelegramCalendar

from .models import Appointment, Doctor, Letter, Patient, Specialization

env = Env()
env.read_env()

CHANNEL = env.int("CHANNEL")
ADMIN = env.int("ADMIN")

bot = telebot.TeleBot(env.str("BOT_TOKEN"), parse_mode="HTML")
extra_datas = {}

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


@bot.message_handler(commands=["start", "send"])
def start(message):
    if message.text == "/start":
        if len(message.text.split()) > 1:
            doc = Doctor.objects.filter(doc_token=message.text.split()[1]).first()
            doc.doc_id = message.from_user.id
            doc.show_img_preview = False
            doc.active = True
            doc.save()
            markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
            btn = types.KeyboardButton(str(_("📋 Менинг қабулим")))
            btn1 = types.KeyboardButton(str(_("👤 Профиль")))
            markup.add(btn).add(btn1)
            bot.send_message(
                message.from_user.id,
                f"Ассалому алайкум доктор {doc.first_name}!\nБу бот сизнинг мавжуд ва янги қабулингизга ёзилган беъморлар ҳақида маълумот беради",
                reply_markup=markup,
            )
        else:
            user = Patient.objects.filter(user_id=message.from_user.id).first()
            doc = Doctor.objects.filter(doc_id=message.from_user.id).first()
            if user:
                if user.active == True:
                    markup = types.ReplyKeyboardMarkup(
                        row_width=2, resize_keyboard=True
                    )
                    btn = types.KeyboardButton("🧾 Қабулга ёзилиш")
                    btn2 = types.KeyboardButton("🚨 Тезкор Алоқа")
                    btn1 = types.KeyboardButton("👤 Профиль")
                    apps = Appointment.objects.filter(
                        patient__user_id=message.from_user.id, active=True
                    )
                    if len(apps) > 0:
                        btn4 = types.KeyboardButton("📋 Қабулни кўриш")
                        markup.add(btn4).add(btn, btn2).add(btn1)
                    else:
                        markup.add(btn, btn2).add(btn1)
                    bot.send_message(
                        message.chat.id,
                        str(_("<b>Шифокор қабулига ёзилиш</b>")),
                        reply_markup=markup,
                    )
                else:
                    user.first_name = message.from_user.first_name
                    user.source = "bot"
                    user.save()
                    text = str(
                        _(
                            f"<b>Ассалому алайкум <i>{message.from_user.first_name}</i>.\nБизнинг хизматлардан фойдаланиш учун аввал рўйҳатдан ўтинг!</b>"
                        )
                    )
                    markup = types.ReplyKeyboardMarkup(
                        row_width=2, resize_keyboard=True
                    )
                    btn = types.KeyboardButton(str(_("📝 Рўйҳатдан ўтиш")))
                    markup.add(btn)
                    bot.send_message(message.from_user.id, text, reply_markup=markup)

            elif doc:
                markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
                btn = types.KeyboardButton(str(_("📋 Менинг қабулим")))
                btn1 = types.KeyboardButton(str(_("🚨 Тезкор Алоқа")))
                markup.add(btn)
                bot.send_message(
                    message.from_user.id,
                    f"Ассалому алайкум доктор {doc.first_name}!",
                    reply_markup=markup,
                )
            else:
                Patient.objects.create(
                    user_id=message.from_user.id,
                    first_name=message.from_user.first_name,
                    source="bot",
                )
                text = str(
                    _(
                        f"<b>Ассалому алайкум <i>{message.from_user.first_name}</i>.\nБизнинг хизматлардан фойдаланиш учун аввал рўйҳатдан ўтинг!</b>"
                    )
                )
                markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
                btn = types.KeyboardButton(str(_("📝 Рўйҳатдан ўтиш")))
                markup.add(btn)
                bot.delete_message(message.from_user.id, message.message.message_id)
                bot.send_message(message.from_user.id, text, reply_markup=markup)
    elif message.text == "/send" and message.from_user.id == ADMIN:
        Letter.objects.create(admin_id=ADMIN, active=True)
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        btn2 = types.KeyboardButton(str(_("🛑 Бекор қилиш")))
        markup.add(btn2)
        msg = bot.send_message(
            message.chat.id,
            "10 белгидан кам бўлмаган ҳабар ёки медиа (видео/расм) юборинг!",
            reply_markup=markup,
        )
        bot.register_next_step_handler(msg, send_process)


@bot.message_handler(func=lambda message: message.text == str(_("📋 Менинг қабулим")))
def doc_appointments(message):
    doc = Doctor.objects.filter(doc_id=message.from_user.id).first()

    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn = types.KeyboardButton(str(_("📋 Менинг қабулим")))
    markup.add(btn)
    if doc:
        apps = Appointment.objects.filter(docworkday__doctor=doc, active=True)
        for app in apps:
            if app.patient.source == "web":
                text = str(
                    _(
                        f"<b>Tartib raqami:</b>  <i>{app.id}</i>\n<b>Ism:</b>  <i>{app.patient.first_name}</i>\n<b>Familya:</b>  <i>{app.patient.last_name}</i>\n<b>Telefon raqam:</b> <i>{app.patient.phone_number}</i>\n<b>Mas'ul shifokor:</b> <i>{app.docworkday.doctor}</i>\n<b>Qabul kuni:</b> <i>{app.docworkday.day.week_day}</i>\n<b>Qabul vaqti:</> <i>{app.time.start_time.strftime('%H:%M')}</i>\n<b>Yaratilgan sana:</b> <i>{app.created}\n{f'Qo`shimcha: {app.complaint}' if len(app.complaint)>0 else '<b>Qo`shimcha</b>: Admin panel orqali ariza yaratildi'}\n</i>"
                    )
                )
            else:
                text = str(
                    _(
                        f"""<b>Tartib raqami:</b>  <i>{app.id}</i>\n<b>Ism:</b>  <i>{app.patient.first_name}</i>\n<b>Familya:</b>  <i>{app.patient.last_name}</i>\n<b>Telefon raqam:</b> <i>{app.patient.phone_number}</i>\n{f'Telegram: @{app.patient.username}' if app.patient.username else f"Telegram: <a href='tg://user?id={app.patient.user_id}'>{app.patient.first_name}</a>"}\n<b>Mas'ul shifokor:</b> <i>{app.docworkday.doctor}</i>\n<b>Qabul kuni:</b> <i>{app.docworkday.day.week_day}</i>\n<b>Qabul vaqti:</> <i>{app.time.start_time.strftime('%H:%M')}</i>\n<b>Yaratilgan sana:</b> <i>{app.created}</i>"""
                    )
                )
            bot.send_message(message.from_user.id, text, reply_markup=markup)
    else:
        bot.send_message(
            message.from_user.id,
            "<b><i>Рўйҳатга олинган қабуллар топилмади!</i></b>",
            reply_markup=markup,
        )


@bot.message_handler(
    func=lambda message: message.text == "🛑 Бекор қилиш" or message.text == "⬅️ Ортга"
)
def cancel(message):
    bot_user = Patient.objects.get(user_id=message.from_user.id)
    app = Appointment.objects.filter(patient=bot_user)
    if bot_user.active != True:
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        btn = types.KeyboardButton(str(_("📝 Рўйҳатдан ўтиш")))
        markup.add(btn)
        bot_user.step = 0
        bot_user.save()
        text = str(
            _(
                f"<i>Ҳурматли {message.from_user.first_name}.\n<b>Бизнинг хизматлардан фойдаланиш учун аввал Рўйҳатдан ўтишингиз шарт!</b></i>"
            )
        )
        bot.send_message(message.from_user.id, text, reply_markup=markup)

    else:
        markup = types.ReplyKeyboardMarkup(
            row_width=2, resize_keyboard=True, one_time_keyboard=True
        )
        btn = types.KeyboardButton("🧾 Қабулга ёзилиш")
        btn2 = types.KeyboardButton("🚨 Тезкор Алоқа")
        btn1 = types.KeyboardButton("👤 Профиль")
        if Appointment.objects.filter(
            patient__user_id=message.from_user.id, active=True
        ):
            btn4 = types.KeyboardButton("📋 Қабулни кўриш")
            markup.add(btn4).add(btn, btn2).add(btn1)
        else:
            markup.add(btn, btn2).add(btn1)

        bot.send_message(
            message.chat.id,
            str(_("<b>Бош сахифа:</b>")),
            reply_markup=markup,
        )


@bot.message_handler(func=lambda message: message.text == str(_("👤 Профиль")))
def profile(message):
    doc = Doctor.objects.filter(doc_id=message.from_user.id).first()
    if doc:
        text = f"""Sizning ma'lumotlaringiz:\nIsm: {doc.first_name}\nFamiliya: {doc.last_name}\nTelefon raqami: {doc.phone_number}\nQo'shimcha ma'lumotlar{doc.about}\nAgar shaxsiy ma`lumotlaringizda xatolik bo`lsa, Adminni habardor qiling"""
        markup = types.InlineKeyboardMarkup(row_width=2)
        b = types.InlineKeyboardButton(
            "Admin bilan bog'lanish", url="http://t.me/dkarimoff96"
        )
        b1 = types.InlineKeyboardButton("🛑 Бекор қилиш", callback_data="back")
        markup.add(b, b1)
    else:
        bot.send_message(
            message.from_user.id, "Фойдаланувчи маълумотларини таҳрирлаш ойнаси"
        )
        patient = Patient.objects.filter(user_id=message.from_user.id).first()
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        b = types.InlineKeyboardButton("♻️ Маълумотларни янгилаш")
        b1 = types.InlineKeyboardButton("🛑 Бекор қилиш")
        markup.add(b).add(b1)
        text = f"""Сизнинг маълумотларингиз:\nИсм: {patient.first_name}\nФамилия: {patient.last_name}\nТелефон рақами: {patient.phone_number}"""
    bot.send_message(message.from_user.id, text, reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == str(_("📋 Қабулни кўриш")))
def checkout(message):
    markup1 = types.ReplyKeyboardMarkup(
        row_width=2, resize_keyboard=True, one_time_keyboard=True
    )
    btn = types.KeyboardButton("⬅️ Ортга")

    markup1.add(btn)
    bot.send_message(
        message.from_user.id,
        "<b><u>Сизнинг аризаларингиз</u></b>",
        reply_markup=markup1,
    )

    markup = types.InlineKeyboardMarkup(row_width=2)
    bot_user = Patient.objects.get(user_id=message.from_user.id)
    apps = Appointment.objects.filter(patient=bot_user)
    for app in apps:
        if app.urgent == True:
            text = f"""<b>‼️Тезкор Алоқа✅ Тартиб рақами:</b>  <i>№{app.id}</i>\n<b>🙍‍♂️ Беъмор:</b> <i>{app.patient.first_name} {app.patient.last_name}</i>\n<b>📞 Телефон рақам:</b> <i>{app.patient.phone_number}</i>\ \n<b>🔰 Яратилган вақти:</b> <i>{(app.created+datetime.timedelta(hours=5)).strftime("%Y-%m-%d %H:%M")}</i>"""
        else:
            text = str(
                _(
                    f"""<b>✅ Тартиб рақами:</b>  <i>№{app.id}</i>\n<b>🙍‍♂️ Беъмор:</b> <i>{app.patient.first_name} {app.patient.last_name}</i>\n<b>📞 Телефон рақам:</b> <i>{app.patient.phone_number}</i>\n<b>👨‍⚕️ Масъул шифокор:</b> <i>{app.doctor}</i>\n<b>📅 Қабул куни:</b> <i>{app.app_date}</i>\n<b>🕔 Қабул соати:</> <i>{app.app_time.strftime('%H:%M')}</i>\n<b>🔰 Яратилган вақти:</b> <i>{(app.created+datetime.timedelta(hours=5)).strftime("%Y-%m-%d %H:%M")}</i>"""
                )
            )
        markup = types.InlineKeyboardMarkup(row_width=2)
        button_text = "❌ Ўчириш"
        button_callback = f"delete|{app.id}"
        button = types.InlineKeyboardButton(button_text, callback_data=button_callback)
        markup.add(button)

        bot.send_message(
            message.from_user.id, text, reply_markup=markup, parse_mode="HTML"
        )


@bot.message_handler(
    func=lambda message: message.text == str(_("📝 Рўйҳатдан ўтиш"))
    or message.text == str(_("♻️ Маълумотларни янгилаш"))
)
def register(message):
    bot_user = Patient.objects.get(user_id=message.from_user.id)
    markup = types.ReplyKeyboardMarkup(
        row_width=1, resize_keyboard=True, one_time_keyboard=True
    )
    btn = types.KeyboardButton(message.from_user.first_name)
    bot_user.step = 1
    bot_user.save()
    markup.add(btn)
    bot.send_message(
        message.from_user.id, str(_("Исмингизни киритинг!")), reply_markup=markup
    )


@bot.message_handler(func=lambda message: message.text == str(_("🚨 Тезкор Алоқа")))
def emergency(message):
    global extra_datas
    extra_datas[message.from_user.id] = {}
    text = str(
        _(
            """Сиз Тезкор Алоқа қисмида сиз қуйидаги муаммолар бўйича биздан шошилинч онлайн консультасия олишингиз мумкин.\n
🔻Қон босимини ошиши
🔻Қон босими пасайиб кетиши
🔻Қон босимини кўтарилиб, тушиб кетиши
🔻Буйракдаги муаммолар (шамоллаш, диабетик нефропатия, буйрак етишмочилиги)
🔻Нафас олиш системасидаги муаммолар
🔻Диабетиклар учун индивидуал программа( овкатланиш тартиби, нималар истеъмол қилиш мумкин эмас, қандай жисмоний фаоллик самарали)
🔻Оёқда музлаш,шиш ва оғриқлар ПОЛИНЕЙРОПАТИЯ, оёк аретрияларида стенозлар, диабетик тўпиқ
🔻Қон суюлтириш усуллари
🔻Юрак сохасида огриклар бўлса
🔻Юрак тез уриб кетиши
🔻Томоққа бирор нарса тиқилганлик хисси
🔻Юрак нотекис уруши
🔻Ўлим хиссини пайдо бўлиши
🔻Юракни секин уруши
🔻Сурункали юрак етишмовчлиги
🔻Сурункали чарчок хисси
🔻Буқоқ бези фаолиятини бузулиши (гипотириоз, гипертириоз)
🔻Ошқозон ичак системасидаги муаммолар
🔻Овқат хазм қилишда қийналиш Зарда бўлиш
🔻Эрталаб уйғонганда оғизда аччик таъм бўлиши
🔻Ич келиш қийинлашиши
📌ПРЕПАРАТЛАР ХАҚИДА МАЛУМОТ ОЛИШ ВА ПРЕПАРАТ ТЎҒРИ ТАНЛАШ."""
        )
    )
    bot_user = Patient.objects.get(user_id=message.from_user.id)
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn = types.KeyboardButton(str(_("➡️ Давом этиш")))
    btn1 = types.KeyboardButton(str(_("🛑 Бекор қилиш")))
    markup.add(btn).add(btn1)
    bot.send_message(message.from_user.id, text, reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == str(_("➡️ Давом этиш")))
def cont(message):
    bot_user = Patient.objects.get(user_id=message.from_user.id)
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn = types.KeyboardButton(str(_("✅ Тасдиқлаш")))
    btn1 = types.KeyboardButton(str(_("🔖 Шикоят матни киритиш")))
    btn2 = types.KeyboardButton(str(_("🛑 Бекор қилиш")))
    bot_user.step = 100
    bot_user.save()
    markup.add(btn, btn1, btn2)
    text = str(
        _(
            f"<b>Тезкор кўрик учун ариза топширувчи беъмор маълумотлари:\nИсми: </b><i>{bot_user.first_name}</i>\n<b>Фамилияси:</b> <i>{bot_user.last_name}</i>\n<b>Телефон рақами:</b> <i>{bot_user.phone_number}</i>\n<b>Шикояти:</b> <i>Тезкор Алоқа!\n\nБарча маълумотларингиз тўгри бўлса ✅ Тасдиқлаш тугмасини босинг!\nP.S: Шикоят матнини киритиш ихтиёри!</i>"
        )
    )
    bot.send_message(message.from_user.id, text, reply_markup=markup)


@bot.message_handler(
    func=lambda message: message.text == str(_("✏️ Шикоят матнини ўзгартириш"))
    or message.text == str(_("🔖 Шикоят матни киритиш"))
)
def make_complaint(message):
    global extra_datas
    bot_user = Patient.objects.get(user_id=message.from_user.id)
    extra_datas[message.from_user.id] = {"complaint": message.text}
    bot_user.step = 200
    bot_user.save()
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn2 = types.KeyboardButton(str(_("🛑 Бекор қилиш")))
    markup.add(btn2)
    bot.send_message(
        message.from_user.id,
        str(_("<i>Шикоят матнини киритинг:</i>")),
        reply_markup=markup,
    )


@bot.message_handler(func=lambda message: message.text == str(_("✅ Тасдиқлаш")))
def confirm(message):
    global extra_datas
    patient = Patient.objects.get(user_id=message.from_user.id)
    complaint = (
        extra_datas[message.from_user.id]["complaint"]
        if "complaint" in extra_datas
        else ""
    )
    app = Appointment.objects.create(
        patient=patient,
        complaint=complaint,
        name=patient.first_name,
        phone_number=patient.phone_number,
        # app_time=datetime.datetime.now().time().strftime("%H:%m"),
        # app_date=datetime.datetime.now().today().strftime("%Y-%m-%d"),
        urgent=True,
        active=True,
        type="bot",
    )
    apps = Appointment.objects.filter(patient=patient)
    markup = types.ReplyKeyboardMarkup(
        row_width=2, resize_keyboard=True, one_time_keyboard=True
    )
    btn = types.KeyboardButton("🧾 Қабулга ёзилиш")
    btn2 = types.KeyboardButton("🚨 Тезкор Алоқа")
    btn1 = types.KeyboardButton("👤 Профиль")
    apps = Appointment.objects.filter(
        patient__user_id=message.from_user.id, active=True
    )
    if len(apps) > 0:
        btn4 = types.KeyboardButton("📋 Қабулни кўриш")
        markup.add(btn4).add(btn, btn2).add(btn1)
    else:
        markup.add(btn, btn2).add(btn1)
    bot.send_message(
        message.chat.id,
        str(
            _(
                "<b><i>Тезкор аризангиз админларга юборилди ва тез орада ҳодимларимиз сиз билан боғланишади.</i></b>"
            )
        ),
        reply_markup=markup,
    )
    text = str(
        _(
            f"<b>Тезкор кўрик учун ариза топширувчи беъмор маълумотлари:\nИсми:</b> <i>{patient.first_name}</i>\n<b>Фамилияси:</b> <i>{patient.last_name}</i>\n<b>Телефон рақами:</b> <i>{patient.phone_number}</i>\n<b>Қўшимча маълумот:</b> <i>Тезкор Алоқа! {complaint}</i>\n<b>Қабул вақти:</b> <i>{(app.created+datetime.timedelta(hours=5)).strftime('%Y-%m-%d %H:%M')}</i>"
        )
    )
    bot.send_message(CHANNEL, text)
    bot.send_message(
        message.chat.id,
        str(_("<b>Шифокор қабулига ёзилиш</b>")),
        reply_markup=markup,
    )


@bot.message_handler(func=lambda message: message.text == str(_("🧾 Қабулга ёзилиш")))
def make_appointment(message):
    fields = Specialization.objects.all()
    markup = types.InlineKeyboardMarkup(row_width=2)
    global extra_datas
    extra_datas[message.from_user.id] = {}
    row_buttons = []
    for field in fields:
        button = types.InlineKeyboardButton(
            field.name, callback_data=f"field|{field.id}"
        )
        row_buttons.append(button)
        if len(row_buttons) == 2:
            markup.add(*row_buttons)
            row_buttons = []

    if len(row_buttons) == 1:
        markup.add(row_buttons[0])

    back = types.InlineKeyboardButton("🛑 Бекор қилиш", callback_data="back")
    markup.add(back)
    bot.send_message(
        message.chat.id, "Қошимча малумот", reply_markup=types.ReplyKeyboardRemove()
    )
    bot.send_message(
        message.chat.id,
        str(
            _(
                "Бу ерга Шифохона ёки сервис хизмат турлари ҳақида қисқача маълумот ёзилиши мумкин"
            )
        ),
        reply_markup=markup,
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("field|"))
def handle_callback_query(call):
    bot.delete_message(call.from_user.id, call.message.message_id)
    global extra_datas
    field_id = call.data.split("|")[1]
    extra_datas[call.from_user.id]["field_id"] = field_id
    markup = types.InlineKeyboardMarkup(row_width=2)
    row_buttons = []
    field = Specialization.objects.get(id=field_id)
    doctors = Doctor.objects.filter(specialization__id=field_id)
    for doctor in doctors:
        button = types.InlineKeyboardButton(
            f"{doctor.first_name} {doctor.last_name}", callback_data=f"doc|{doctor.id}"
        )
        row_buttons.append(button)
        if len(row_buttons) == 2:
            markup.add(*row_buttons)
            row_buttons = []

    if len(row_buttons) == 1:
        markup.add(row_buttons[0])

    back = types.InlineKeyboardButton("🛑 Бекор қилиш", callback_data="back")
    markup.add(back)
    bot.send_message(
        call.from_user.id,
        field.description,
        reply_markup=markup,
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("doc|"))
def handle_callback_query(call: CallbackQuery):
    bot.delete_message(call.from_user.id, call.message.message_id)

    global extra_datas
    doc_id = call.data.split("|")[1]
    extra_datas[call.from_user.id]["doctor_id"] = doc_id
    doc = Doctor.objects.get(id=doc_id)
    calendar, step = DetailedTelegramCalendar().build()
    photo_message = bot.send_photo(call.from_user.id, doc.image, caption=doc.about)
    extra_datas[call.from_user.id]["photo_message_id"] = photo_message.message_id
    bot.send_message(call.from_user.id, "Қабул кунини танланг:", reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func())
def cal(c: CallbackQuery):
    result, key, step = DetailedTelegramCalendar().process(c.data)
    if not result and key:
        bot.edit_message_text(
            f"Tanlang {LSTEP[step]}",
            c.message.chat.id,
            c.message.message_id,
            reply_markup=key,
        )
    elif result:
        global extra_datas
        extra_datas[c.from_user.id]["date"] = result
        extra_datas[c.from_user.id]["callback_query_id"] = c.id
        show_available_times(c.from_user.id, c.message.chat.id, c.message.message_id)


def show_available_times(user_id, chat_id, message_id):
    global extra_datas
    day = extra_datas[user_id]["date"].weekday()
    selected_date = extra_datas[user_id]["date"]
    available_times_weekday = [
        "08:00",
        "08:20",
        "08:40",
        "09:00",
        "09:20",
        "09:40",
        "10:00",
        "10:20",
        "10:40",
        "11:00",
        "11:20",
        "12:40",
        "13:00",
        "13:40",
        "14:00",
        "14:20",
        "14:40",
        "15:00",
        "15:20",
        "15:40",
        "16:00",
    ]
    available_times_saturday = [
        "08:00",
        "08:20",
        "08:40",
        "09:00",
        "09:20",
        "09:40",
        "10:00",
        "10:20",
        "10:40",
        "11:00",
        "11:20",
        "12:40",
        "13:00",
    ]

    if day == 5:  # Saturday (0 is Monday, 1 is Tuesday, ..., 5 is Saturday)
        available_times = available_times_saturday
    else:
        available_times = available_times_weekday

    app = (
        Appointment.objects.filter(
            app_date=extra_datas[user_id]["date"].strftime("%Y-%m-%d"),
            doctor__id=extra_datas[user_id]["doctor_id"],
        )
        .values_list("app_time", flat=True)
        .distinct()
    )
    current_time = datetime.datetime.now().strftime("%H:%M")
    booked_times = [time.strftime("%H:%M") for time in app]
    available_times = [time for time in available_times if time not in booked_times]
    if selected_date == datetime.datetime.now().date():
        available_times = [time for time in available_times if time >= current_time]

    markup = types.InlineKeyboardMarkup(row_width=3)
    buttons = [
        types.InlineKeyboardButton(time, callback_data=f"time|{time}")
        for time in available_times
    ]
    back = types.InlineKeyboardButton("🛑 Бекор қилиш", callback_data="back")
    markup.add(*buttons)
    markup.add(back)
    doc = Doctor.objects.get(id=extra_datas[user_id]["doctor_id"])
    if not buttons:
        bot.answer_callback_query(
            callback_query_id=extra_datas[user_id]["callback_query_id"],
            text=f"Кечирасиз! Ушбу кун учун шифокор {doc.first_name} {doc.last_name}нинг бўш вақтлари топилмади",
            show_alert=True,
        )
    else:
        photo_message_id = extra_datas[user_id]["photo_message_id"]
        bot.delete_message(chat_id, photo_message_id)
        bot.edit_message_text(
            text="Мавжуд вақтни танланг:",
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=markup,
        )


@bot.callback_query_handler(func=lambda call: call.data.startswith("time|"))
def call_data(call: CallbackQuery):
    bot.delete_message(call.from_user.id, call.message.message_id)

    time = call.data.split("|")[1]
    global extra_datas
    extra_datas[call.from_user.id]["time"] = time
    user = Patient.objects.get(user_id=call.from_user.id)
    doctor = Doctor.objects.get(id=extra_datas[call.from_user.id]["doctor_id"])
    app = Appointment.objects.create(
        doctor=doctor,
        patient=user,
        app_date=extra_datas[call.from_user.id]["date"],
        app_time=datetime.datetime.strptime(
            extra_datas[call.from_user.id]["time"], "%H:%M"
        ).time(),
        active=True,
        type="bot",
    )
    markup = types.ReplyKeyboardMarkup(
        row_width=2, resize_keyboard=True, one_time_keyboard=True
    )
    btn = types.KeyboardButton("🧾 Қабулга ёзилиш")
    btn2 = types.KeyboardButton("🚨 Тезкор Алоқа")
    btn1 = types.KeyboardButton("👤 Профиль")
    if Appointment.objects.filter(patient__user_id=call.from_user.id, active=True):
        btn4 = types.KeyboardButton("📋 Қабулни кўриш")
        markup.add(btn4).add(btn, btn2).add(btn1)
    else:
        markup.add(btn, btn2).add(btn1)
    text = f"""✅ Аризангиз қабул қилинди!\n❇️ Ариза тартиб рақами: №{app.id}\n🙍‍♂️ Беъмор: {app.patient.first_name} {app.patient.last_name}\n👨‍⚕️ Масъул шифокор: {app.doctor.first_name} {app.doctor.last_name}\n📅 Қабул куни: {extra_datas[call.from_user.id]['date']}\n🕔 Қабул соати: {extra_datas[call.from_user.id]['time']}\n🔰 Яратилган вақти {(app.created+datetime.timedelta(hours=5)).strftime("%Y-%m-%d %H:%M")}"""
    bot.send_message(call.from_user.id, text, reply_markup=markup)


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot_user = Patient.objects.get(user_id=message.from_user.id)
    if len(message.text) > 0 and bot_user.step == 1:
        bot_user.first_name = message.text
        bot_user.step = 2
        bot_user.save()
        bot.send_message(message.chat.id, str(_("Фамилиянгизни киритинг:")))

    elif len(message.text) > 0 and bot_user.step == 2:
        bot_user.last_name = message.text
        bot_user.save()
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add(
            types.KeyboardButton(
                str(_("📞 Телефон рақамни улашиш")), request_contact=True
            )
        )
        bot.send_message(
            message.chat.id,
            str(_("Телефон рақамингизни киритинг:")),
            reply_markup=markup,
        )

    elif bot_user.step == 200 and len(message.text) > 0:
        global extra_datas
        extra_datas[message.from_user.id]["complaint"] = message.text
        bot_user = Patient.objects.get(user_id=message.from_user.id)
        bot_user.save()
        text = str(
            _(
                f"Тезкор кўрик учун ариза топширувчи беъмор маълумотлари:\nИсми: {bot_user.first_name}\nФамилияси: {bot_user.last_name}\nТелефон рақами: {bot_user.phone_number}\nҚўшимча маълумот: Тезкор Алоқа! {message.text}"
            )
        )
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        btn = types.KeyboardButton(str(_("✅ Тасдиқлаш")))
        btn1 = types.KeyboardButton(str(_("✏️ Шикоят матнини ўзгартириш")))
        btn2 = types.KeyboardButton(str(_("🛑 Бекор қилиш")))
        bot_user.step = 100
        bot_user.save()
        markup.add(btn, btn1, btn2)
        bot.send_message(message.from_user.id, text, reply_markup=markup)


@bot.message_handler(content_types=["contact"])
def contact(message):
    bot_user = Patient.objects.get(user_id=message.from_user.id)

    if message.contact is not None and message.contact.phone_number:
        phone_number = message.contact.phone_number
        bot_user.phone_number = phone_number
        bot_user.step = 3
        bot_user.active = True
        bot_user.save()
        markup = types.ReplyKeyboardMarkup(
            row_width=2, resize_keyboard=True, one_time_keyboard=True
        )
        btn = types.KeyboardButton(str(_("🧾 Қабулга ёзилиш")))
        btn2 = types.KeyboardButton(str(_("🚨 Тезкор Алоқа")))
        btn3 = types.KeyboardButton(str(_("👤 Профиль")))

        if Appointment.objects.filter(patient__user_id=message.from_user.id):
            btn1 = types.KeyboardButton(str(_("📋 Қабулни кўриш")))
            markup.add(btn1)
        markup.add(btn, btn2, btn3)
        bot.send_message(
            message.chat.id, str(_(f"Телефон рақам қабул қилинди: {phone_number}"))
        )
        bot.send_message(
            message.chat.id,
            str(_("Рўйҳатдан ўтиш муваффаққиятли якунланди!")),
            reply_markup=markup,
        )


@bot.callback_query_handler(func=lambda call: call.data.startswith("delete|"))
def delete_verification(call: CallbackQuery):
    app_id = call.data.split("|")[1]

    # Show a pop-up confirmation notification with "Yes" and "No" buttons
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    yes_button = types.InlineKeyboardButton(
        "Ҳа", callback_data=f"confirm_delete|{app_id}|{call.message.message_id}|yes"
    )
    no_button = types.InlineKeyboardButton(
        "Йўқ", callback_data=f"confirm_delete|{app_id}|no"
    )
    keyboard.add(yes_button, no_button)
    bot.send_message(
        call.from_user.id,
        f"⁉️ Сиз №{app_id} тартиб рақамли қабулни ўчириб юбормоқчимисиз?",
        reply_markup=keyboard,
    )


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("confirm_delete|")
    and call.data.endswith("|yes")
)
def delete_app_yes(call: CallbackQuery):
    app_id = call.data.split("|")[1]
    app_msg_id = call.data.split("|")[2]
    Appointment.objects.filter(id=app_id).delete()
    bot.delete_message(call.from_user.id, call.message.message_id)
    bot.delete_message(call.from_user.id, app_msg_id)


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("confirm_delete|")
    and call.data.endswith("|no")
)
def delete_app_no(call: CallbackQuery):
    bot.delete_message(call.from_user.id, call.message.message_id)


@bot.callback_query_handler(func=lambda call: call.data == "back")
def back(call: CallbackQuery):
    bot.delete_message(call.from_user.id, call.message.message_id)
    if "photo_message_id" in extra_datas[call.from_user.id]:
        bot.delete_message(
            call.from_user.id, extra_datas[call.from_user.id]["photo_message_id"]
        )
        del extra_datas[call.from_user.id]["photo_message_id"]
    markup = types.ReplyKeyboardMarkup(
        row_width=2, resize_keyboard=True, one_time_keyboard=True
    )
    btn = types.KeyboardButton("🧾 Қабулга ёзилиш")
    btn2 = types.KeyboardButton("🚨 Тезкор Алоқа")
    btn1 = types.KeyboardButton("👤 Профиль")
    if Appointment.objects.filter(patient__user_id=call.from_user.id, active=True):
        btn4 = types.KeyboardButton("📋 Қабулни кўриш")
        markup.add(btn4).add(btn, btn2).add(btn1)
    else:
        markup.add(btn, btn2).add(btn1)
    bot.send_message(call.from_user.id, "<b>Бош сахифа:</b>", reply_markup=markup)


def send_process(message):
    if message.text == "🛑 Бекор қилиш":
        Letter.objects.filter(active=True, admin_id=message.from_user.id).delete()
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        btn = types.KeyboardButton("Button")
        markup.add(btn)
        bot.send_message(
            message.from_user.id, "Ҳабар юбориш бекор қилинди!", reply_markup=markup
        )
    else:
        letter = Letter.objects.filter(admin_id=ADMIN, active=True).last()
        letter.message_id = message.message_id
        letter.save()
        current = letter.current
        chat_id = message.chat.id
        users = Patient.objects.all()[current : current + 50]
        success = 0
        fail = 0
        for user in users:
            user_id = user.user_id
            try:
                bot.copy_message(user_id, chat_id, message.message_id)
                success += 1
            except ApiTelegramException:
                fail += 1
        letter.current = current + 50
        letter.count = letter.count + success
        letter.save()
        if letter.current >= len(Patient.objects.all()):
            markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
            btn = types.KeyboardButton("⬅️ Ортга")
            markup.add(btn)
            us = len(Patient.objects.all())
            total = letter.count
            bot.send_message(
                int(ADMIN),
                f"<b><u>Ҳабар юборишда якунланди:</u></b>\n<b>Жами фойдаланувчилар сони:</b> {us}\n<b>Мувафаққиятли юборилган ҳабар сони:</b> {total}\n<b>Мувафаққияциз юборилган ҳабар сони:</b> {us - total}",
                reply_markup=markup,
            )
            letter.active = False
            letter.save()
            response = HttpResponse()
            response.write("<h1>Ҳабар юборилиши мувофаққиятли якунланди!</h1>")
            return response

        response = HttpResponse()
        response.write("<h1>Ҳабар юборилмоқда!</h1>")
        return response
