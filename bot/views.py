import telebot
from django.shortcuts import HttpResponse
from django.utils.translation import activate
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from environs import Env
from telebot import types
from .models import Appointment, Doctor, Patient, Letter, Specialization
from telebot.apihelper import ApiTelegramException
import datetime
from telebot.types import CallbackQuery
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
            btn = types.KeyboardButton(str(_("Mening qabulim")))
            btn1 = types.KeyboardButton(str(_("Profil")))
            markup.add(btn).add(btn1)
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
                    markup = types.ReplyKeyboardMarkup(
                        row_width=2, resize_keyboard=True
                    )
                    btn = types.KeyboardButton(str(_("Qabulga yozilish")))
                    btn1 = types.KeyboardButton(str(_("Tezkor Aloqa")))
                    btn2 = types.KeyboardButton(str(_("Profil")))
                    markup.add(btn, btn1, btn2)
                    bot.send_message(
                        message.chat.id,
                        str(_("<b>Shifokor qabuliga yozilish</b>")),
                        reply_markup=markup,
                    )
                else:
                    user.first_name = message.from_user.first_name
                    user.username = (
                        message.from_user.username if message.from_user.username else ""
                    )
                    user.first_name = message.from_user.first_name
                    user.source = "bot"
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
                btn1 = types.KeyboardButton(str(_("Tezkor Aloqa")))
                markup.add(btn)
                bot.send_message(
                    message.from_user.id,
                    f"Assalomu alaykum doktor {doc.first_name}!",
                    reply_markup=markup,
                )
            else:
                Patient.objects.create(
                    user_id=message.from_user.id,
                    username=message.from_user.username
                    if message.from_user.username
                    else "",
                    first_name=message.from_user.first_name,
                    source="bot",
                )
                text = "Tinlni tanlang\nТинлни танланг"
                markup = types.InlineKeyboardMarkup(row_width=2)
                b = types.InlineKeyboardButton("Lotin", callback_data="en")
                b1 = types.InlineKeyboardButton("Кирилл", callback_data="ru")
                markup.add(b, b1)
                bot.send_message(message.chat.id, text, reply_markup=markup)
    elif message.text == "/send" and message.from_user.id == ADMIN:
        Letter.objects.create(admin_id=ADMIN, active=True)
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        btn2 = types.KeyboardButton(str(_("🛑Bekor qilish")))
        markup.add(btn2)
        msg = bot.send_message(
            message.chat.id,
            "10 belgidan kam bo`lmagan habar yoki media (video/rasm) yuboring!",
            reply_markup=markup,
        )
        bot.register_next_step_handler(msg, send_process)


@bot.message_handler(func=lambda message: message.text == str(_("Mening qabulim")))
def doc_appointments(message):
    doc = Doctor.objects.filter(doc_id=message.from_user.id).first()

    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn = types.KeyboardButton(str(_("Mening qabulim")))
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
            "<b><i>Ro`yhatga olingan qabullar topilmadi!</i></b>",
            reply_markup=markup,
        )


@bot.message_handler(func=lambda message: message.text == str(_("🛑Bekor qilish")))
def cancel(message):
    bot_user = Patient.objects.get(user_id=message.from_user.id)
    activate(bot_user.language)
    app = Appointment.objects.filter(patient=bot_user)
    if bot_user.active != True:
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        btn = types.KeyboardButton(str(_("Ro`yhatdan o`tish")))
        markup.add(btn)
        bot_user.step = 0
        bot_user.save()
        text = str(
            _(
                f"<i>Hurmatli {message.from_user.first_name}.\n<b>Bizning xizmatlardan foydalanish uchun avval ro`yhatdan o`tishingiz shart!</b></i>"
            )
        )
        bot.send_message(message.from_user.id, text, reply_markup=markup)

    else:
        markup = types.ReplyKeyboardMarkup(
            row_width=2, resize_keyboard=True, one_time_keyboard=True
        )
        btn = types.KeyboardButton(str(_("Qabulga yozilish")))
        btn1 = types.KeyboardButton(str(_("Tezkor Aloqa")))
        btn3 = types.KeyboardButton(str(_("Profil")))
        markup.add(btn, btn1, btn3)
        if len(app) > 0:
            btn4 = types.KeyboardButton(str(_("Qabulni ko`rish")))
            markup.add(btn4)

        bot.send_message(
            message.chat.id,
            str(_("<b>Shifokor qabuliga yozilish</b>")),
            reply_markup=markup,
        )


@bot.message_handler(func=lambda message: message.text == str(_("Profil")))
def profile(message):
    doc = Doctor.objects.filter(doc_id=message.from_user.id).first()
    if doc:
        text = f"""Sizning ma'lumotlaringiz:\nIsm: {doc.first_name}\nFamiliya: {doc.last_name}\nTelefon raqami: {doc.phone_number}\nQo'shimcha ma'lumotlar{doc.about}\nAgar shaxsiy ma`lumotlaringizda xatolik bo`lsa, Adminni habardor qiling"""
        markup = types.InlineKeyboardMarkup(row_width=2)
        b = types.InlineKeyboardButton(
            "Admin bilan bog'lanish", url="http://t.me/dkarimoff96"
        )
        b1 = types.InlineKeyboardButton("🛑Bekor qilish", callback_data="back")
        markup.add(b, b1)
    else:
        bot.send_message(
            message.from_user.id, "Foydalanuvchi ma`lumotlarini tahrirlash oynasi"
        )
        patient = Patient.objects.filter(user_id=message.from_user.id).first()
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        b = types.InlineKeyboardButton("Ma`lumotlarni yangilash")
        b1 = types.InlineKeyboardButton("🛑Bekor qilish")
        markup.add(b).add(b1)
        text = f"""Sizning ma'lumotlaringiz:\nIsm: {patient.first_name}\nFamiliya: {patient.last_name}\nTelefon raqami: {patient.phone_number}"""
    bot.send_message(message.from_user.id, text, reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == str(_("Qabulni ko`rish")))
def checkout(message):
    markup = types.ReplyKeyboardMarkup(
        row_width=2, resize_keyboard=True, one_time_keyboard=True
    )
    btn = types.KeyboardButton(str(_("Qabulga yozilish")))
    btn1 = types.KeyboardButton(str(_("Tezkor Aloqa")))
    btn3 = types.KeyboardButton(str(_("Profil")))
    btn4 = types.KeyboardButton(str(_("Qabulni ko`rish")))
    markup.add(btn, btn1, btn4).add(btn3)
    bot_user = Patient.objects.get(user_id=message.from_user.id)
    activate(bot_user.language)
    apps = Appointment.objects.filter(patient=bot_user)
    bot.send_message(
        message.from_user.id, "<b><u>Sizning arizalaringiz</u></b>", reply_markup=markup
    )
    for app in apps:
        if app.urgent == True:
            text = str(
                _(
                    f"<u><b>‼️Tezkor qabul arizasi.</b></u>\n<b>Tartib raqami:</b>  {app.id}\n<b>Ismi:</b>  <i>{app.patient.first_name}</i>\n<b>Familiyasi:</b> <i>{app.patient.last_name}</i>\n<b>Telefon raqam:</b>  <i>{app.patient.phone_number}</i>\n{f'<b>Telegram:</b> <i>@{app.patient.username}</i>' if app.patient.username else ''}\n<b>Shikoyat matni:</b> <i>Tezkor aloqa! {app.complaint}</i>\n<b>Yaratilgan vaqti:</b> <i>{app.created}</i>"
                )
            )
        else:
            text = str(
                _(
                    f"<b>Tartib raqami:</b>  <i>{app.id}</i>\n<b>Ism:</b>  <i>{app.patient.first_name}</i>\n<b>Familya:</b>  <i>{app.patient.last_name}</i>\n<b>Telefon raqam:</b> <i>{app.patient.phone_number}</i>\n{f'Telegram: @{app.patient.username}' if app.patient.username else ''}\n<b>Mas'ul shifokor:</b> <i>{app.docworkday.doctor}</i>\n<b>Qabul kuni:</b> <i>{app.docworkday.day.week_day}</i>\n<b>Qabul vaqti:</> <i>{app.time.start_time.strftime('%H:%M')}</i>\n<b>Yaratilgan vaqti:</b> <i>{app.created}</i>"
                )
            )
        bot.send_message(message.from_user.id, text, reply_markup=markup)


@bot.message_handler(
    func=lambda message: message.text == str(_("Ro`yhatdan o`tish"))
    or message.text == str(_("Ma`lumotlarni yangilash"))
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
        message.from_user.id, str(_("Ismingizni kiriting!")), reply_markup=markup
    )


@bot.message_handler(func=lambda message: message.text == str(_("Tezkor Aloqa")))
def emergency(message):
    global extra_datas
    extra_datas[message.from_user.id] = {}
    text = str(
        _(
            """Siz tezkor aloqa qismida siz quyidagi muammolar bo‘yicha bizdan shoshilinch onlayn konsultasiya olishingiz mumkin.\n
🔻Qon bosimini oshishi
🔻Qon bosimi pasayib ketishi
🔻Qon bosimini ko‘tarilib, tushib ketishi
🔻Buyrakdagi muammolar (shamollash, diabetik nefropatiya, buyrak yetishmochiligi)
🔻Nafas olish sistemasidagi muammolar
🔻Xansirash
🔻Nafas yetishmasligi
🔻Surunkali bronxit
🔻Pnevmoniya
🔻XOBL
🔻Branxial astma
🔻Kandli diabet 2-tip
🔻Diabetiklar uchun individual programma( ovkatlanish tartibi, nimalar iste'mol qilish mumkin emas, qanday jismoniy faollik samarali)
🔻Oyoqda muzlash,shish va og'riqlar POLINEYROPATIYa, oyok aretriyalarida stenozlar, diabetik to‘piq
🔻Qon suyultirish usullari
🔻Yurak soxasida ogriklar bo‘lsa
🔻Yurak tez urib ketishi
🔻Tomoqqa biror narsa tiqilganlik xissi
🔻Yurak notekis urushi
🔻Ulim xissini paydo bo'lishi
🔻Yurakni sekin urushi
🔻Surunkali yurak yetishmovchligi
🔻Surunkali charchok xissi
🔻Anemiya (kam qonlik)
🔻Buqoq bezi faoliyatini buzulishi (gipotirioz, gipertirioz)
🔻Oshqozon ichak sistemasidagi muammolar
🔻Qorinni dam bulishi
🔻Ovqat xazm qilishda qiynalish Zarda bo'lish
🔻Ertalab uyg'onganda og'izda achchik ta'm bo'lishi
🔻Ich kelish qiyinlashishi
📌PREPARATLAR XAQIDA MALUMOT OLISH VA PREPARAT TO'G'RI TANLASH."""
        )
    )
    bot_user = Patient.objects.get(user_id=message.from_user.id)
    activate(bot_user.language)
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn = types.KeyboardButton(str(_("Davom etish")))
    btn1 = types.KeyboardButton(str(_("🛑Bekor qilish")))
    markup.add(btn).add(btn1)
    bot.send_message(message.from_user.id, text, reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == str(_("Davom etish")))
def cont(message):
    bot_user = Patient.objects.get(user_id=message.from_user.id)
    activate(bot_user.language)
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn = types.KeyboardButton(str(_("Tasdiqlash")))
    btn1 = types.KeyboardButton(str(_("Shikoyat matni kiritish")))
    btn2 = types.KeyboardButton(str(_("🛑Bekor qilish")))
    bot_user.step = 100
    bot_user.save()
    markup.add(btn, btn1, btn2)
    text = str(
        _(
            f"<b>Tezkor ko`rik uchun ariza topshiruvchi be`mor ma`lumotlari:\nIsmi: </b><i>{bot_user.first_name}</i>\n<b>Familyasi:</b> <i>{bot_user.last_name}</i>\n<b>Telefon raqami:</b> <i>{bot_user.phone_number}</i>\n<b>Shikoyati:</b> <i>Tezkor aloqa!\n\nBarcha ma`lumotlaringiz to`gri bo`lsa tasdiqlash tugmasini bosing!\nP.S: Shikoyat matnini kiritish ixtiyori!</i>"
        )
    )
    bot.send_message(message.from_user.id, text, reply_markup=markup)


@bot.message_handler(
    func=lambda message: message.text == str(_("Shikoyat matni kiritish"))
)
def make_complaint(message):
    global extra_datas
    bot_user = Patient.objects.get(user_id=message.from_user.id)
    extra_datas[message.from_user.id] = {"complaint": message.text}
    bot_user.step = 200
    activate(bot_user.language)
    bot_user.save()
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn2 = types.KeyboardButton(str(_("🛑Bekor qilish")))
    markup.add(btn2)
    bot.send_message(
        message.from_user.id,
        str(_("<i>Shikoyat matnini kiriting:</i>")),
        reply_markup=markup,
    )


@bot.message_handler(
    func=lambda message: message.text == str(_("Shikoyatni o`zgartirish"))
)
def change_complaint(message):
    global extra_datas
    bot_user = Patient.objects.get(user_id=message.from_user.id)
    extra_datas[message.from_user.id]["complaint"] = message.text
    activate(bot_user.language)
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn = types.KeyboardButton(str(_("Tasdiqlash")))
    btn1 = types.KeyboardButton(str(_("Shikoyatni o`zgartirish")))
    btn2 = types.KeyboardButton(str(_("🛑Bekor qilish")))
    markup.add(btn, btn1, btn2)
    text = str(
        _(
            f"<b>Tezkor ko`rik uchun ariza topshiruvchi be`mor ma`lumotlari:\nIsmi: </b><i>{bot_user.first_name}<i>\n<b>Familyasi: </b><i>{bot_user.last_name}</i>\n<b>Telefon raqami:</b> <i>{bot_user.phone_number}</i>\n<b>Shikoyati:</b> <i>Tezkor aloqa!{message.text}</i>\n\n<i><b>Barcha ma`lumotlaringiz to`gri bo`lsa tasdiqlash tugmasini bosing!</b></i>"
        )
    )
    bot.send_message(message.from_user.id, text, reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == str(_("Tasdiqlash")))
def confirm(message):
    global extra_datas
    patient = Patient.objects.filter(user_id=message.from_user.id)[0]
    complaint = (
        extra_datas[message.from_user.id]["complaint"]
        if "complaint" in extra_datas
        else ""
    )
    app = Appointment.objects.create(
        patient=patient, complaint=complaint, urgent=True, active=True, type="bot"
    )
    apps = Appointment.objects.filter(patient=patient)
    activate(patient.language)
    markup = types.ReplyKeyboardMarkup(
        row_width=2, resize_keyboard=True, one_time_keyboard=True
    )
    btn = types.KeyboardButton(str(_("Qabulga yozilish")))
    btn1 = types.KeyboardButton(str(_("Tezkor Aloqa")))
    btn3 = types.KeyboardButton(str(_("Profil")))
    markup.add(btn, btn1)

    if len(app) > 0:
        btn4 = types.KeyboardButton(str(_("Qabulni ko`rish")))
        markup.add(btn4)
    markup.add(btn3)
    bot.send_message(
        message.chat.id,
        str(
            _(
                "<b><i>Tezkor arizangiz adminlarga yuborildi va tez orada hodimlarimiz siz bilan bog`lanishadi.</i></b>"
            )
        ),
        reply_markup=markup,
    )
    text = str(
        _(
            f"<b>Tezkor ko`rik uchun ariza topshiruvchi be`mor ma`lumotlari:\nIsmi:</b> <i>{patient.first_name}</i>\n<b>Familyasi:</b> <i>{patient.last_name}</i>\n{f'Telegram: @{app.patient.username}' if app.patient.username else ''}\n<b>Telefon raqami:</b> <i>{patient.phone_number}</i>\n<b>Qo`shimcha ma`lumot:</b> <i>Tezkor aloqa! {complaint}</i>\n<b>Qabul vaqti:</b> <i>{app.created}</i>"
        )
    )
    bot.send_message(CHANNEL, text)
    bot.send_message(
        message.chat.id,
        str(_("<b>Shifokor qabuliga yozilish</b>")),
        reply_markup=markup,
    )


@bot.message_handler(func=lambda message: message.text == str(_("Qabulga yozilish")))
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
        message.chat.id,
        str(
            _(
                "Bu yerga Shifoxona yoki servis xizmat turlari haqida qisqacha ma`lumot yozilishi mumkin"
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
            doctor.first_name, callback_data=f"doc|{doctor.id}"
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
        "field.description",
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
    photo_message = bot.send_photo(
        call.from_user.id, doc.image, caption=doc.information
    )

    extra_datas[call.from_user.id]["photo_message_id"] = photo_message.message_id
    # Second, send the caption and the calendar as a new message
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

    current_time = (datetime.datetime.now() + datetime.timedelta(hours=5)).strftime(
        "%H:%M"
    )
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
    btn3 = types.KeyboardButton("👤 Профиль")
    if Appointment.objects.filter(patient__user_id=call.from_user.id, active=True):
        btn4 = types.KeyboardButton("🔰 Қабулни кўриш")
        markup.add(btn, btn4, btn3)
    else:
        markup.add(btn).add(btn3)
    text = f"""✅ Аризангиз қабул қилинди!\n❇️ Ариза тартиб рақами: №{app.id}\n🙍‍♂️ Беъмор: {app.patient.first_name} {app.patient.last_name}\n👨‍⚕️ Масъул шифокор: {app.doctor.first_name} {app.doctor.last_name}\n📅 Қабул куни: {extra_datas[call.from_user.id]['date']}\n🕔 Қабул соати: {extra_datas[call.from_user.id]['time']}\n🔰 Яратилган вақти {(app.created+datetime.timedelta(hours=5)).strftime("%Y-%m-%d %H:%M")}"""
    bot.send_message(call.from_user.id, text, reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot_user = Patient.objects.get(user_id=message.from_user.id)
    activate(bot_user.language)
    if len(message.text) > 0 and bot_user.step == 1:
        bot_user.first_name = message.text
        bot_user.step = 2
        bot_user.save()
        bot.send_message(message.chat.id, str(_("Familyangizni kiriting:")))

    elif len(message.text) > 0 and bot_user.step == 2:
        bot_user.last_name = message.text
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

    elif bot_user.step == 200 and len(message.text) > 0:
        global extra_datas
        extra_datas[message.from_user.id]["complaint"] = message.text
        bot_user = Patient.objects.get(user_id=message.from_user.id)
        activate(bot_user.language)
        bot_user.save()
        text = str(
            _(
                f"Tezkor ko`rik uchun ariza topshiruvchi be`mor ma`lumotlari:\nIsmi: {bot_user.first_name}\nFamilyasi: {bot_user.last_name}\nTelefon raqami: {bot_user.phone_number}\nQo`shimcha ma`lumot: Tezkor aloqa! {message.text}"
            )
        )
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        btn = types.KeyboardButton(str(_("Tasdiqlash")))
        btn1 = types.KeyboardButton(str(_("Shikoyat matni o'zgartirish")))
        btn2 = types.KeyboardButton(str(_("🛑Bekor qilish")))
        bot_user.step = 100
        markup.add(btn, btn1, btn2)
        bot.send_message(message.from_user.id, text, reply_markup=markup)


@bot.message_handler(content_types=["contact"])
def contact(message):
    bot_user = Patient.objects.get(user_id=message.from_user.id)
    activate(bot_user.language)

    if message.contact is not None and message.contact.phone_number:
        phone_number = message.contact.phone_number
        bot_user.phone_number = phone_number
        bot_user.step = 3
        bot_user.active = True
        bot_user.save()
        markup = types.ReplyKeyboardMarkup(
            row_width=2, resize_keyboard=True, one_time_keyboard=True
        )
        btn = types.KeyboardButton(str(_("Qabulga yozilish")))
        btn2 = types.KeyboardButton(str(_("Tezkor Aloqa")))
        btn3 = types.KeyboardButton(str(_("Profil")))

        if Appointment.objects.filter(patient__user_id=message.from_user.id):
            btn1 = types.KeyboardButton(str(_("Qabulni ko`rish")))
            markup.add(btn1)
        markup.add(btn, btn2, btn3)
        bot.send_message(
            message.chat.id, str(_(f"Telefon raqam qabul qilindi: {phone_number}"))
        )
        bot.send_message(
            message.chat.id,
            str(_("Ro`yhatdan o`tish muvaffaqqiyatli yakunlandi!")),
            reply_markup=markup,
        )


# @bot.callback_query_handler(func=lambda call: call.data.startswith("doctor|"))
# def handle_callback_query(call):
#     global extra_datas
#     doc_id = call.data.split("|")[1]
#     extra_datas[call.from_user.id]["doctor_id"] = doc_id
#     docworkdays = DocWorkDay.objects.filter(doctor__pk=doc_id)
#     markup = types.InlineKeyboardMarkup(row_width=2)
#     row_buttons = []

#     for docworkday in docworkdays:
#         times = docworkday.times.all()
#         for time in times:
#             if not Appointment.objects.filter(
#                 docworkday=docworkday, time=time, active=True
#             ).exists():
#                 button = types.InlineKeyboardButton(
#                     docworkday.day.week_day, callback_data=f"day|{docworkday.id}"
#                 )
#                 row_buttons.append(button)
#                 if len(row_buttons) == 2:
#                     markup.add(*row_buttons)
#                 break

#     text = f"<i>Shifokor: {Doctor.objects.get(id=doc_id).about}</i>"
#     if len(row_buttons) == 0:
#         text = "<i>Shifokorning qabul qilish vaqtlari mavjud emas</i>"
#     elif len(row_buttons) == 1:
#         text = f"<i>Shifokor: {Doctor.objects.get(id=doc_id).about}</i>"
#         markup.add(row_buttons[0])

#     back = types.InlineKeyboardButton("🛑Bekor qilish", callback_data="back")
#     markup.add(back)
#     bot.delete_message(call.from_user.id, message_id=call.message.message_id)
#     bot.send_message(call.from_user.id, text, reply_markup=markup)


# @bot.callback_query_handler(func=lambda call: call.data.startswith("day|"))
# def handle_callback_query(call):
#     day_id = call.data.split("|")[1]
#     weekday = DocWorkDay.objects.filter(pk=day_id).first()
#     times: list[Time] = weekday.times.all()
#     markup = types.InlineKeyboardMarkup(row_width=2)
#     row_buttons = []
#     for time in times:
#         if Appointment.objects.filter(
#             docworkday_id=day_id, time=time, active=True
#         ).exists():
#             continue
#         button = types.InlineKeyboardButton(
#             time.start_time.strftime("%H:%M"), callback_data=f"time|{time.id}|{day_id}"
#         )
#         row_buttons.append(button)
#         if len(row_buttons) == 2:
#             markup.add(*row_buttons)
#             row_buttons = []
#     if len(row_buttons) == 1:
#         markup.add(row_buttons[0])
#     back = types.InlineKeyboardButton("🛑Bekor qilish", callback_data="back")
#     markup.add(back)
#     bot.delete_message(call.from_user.id, message_id=call.message.message_id)

#     bot.send_message(
#         call.from_user.id,
#         "<i>Mavjud vaqtlardan birini tanlang</i>",
#         reply_markup=markup,
#     )


# @bot.callback_query_handler(func=lambda call: call.data.startswith("time|"))
# def handle_callback_query(call):
#     global extra_datas
#     extra_datas[call.from_user.id]["time_id"] = call.data.split("|")[1]
#     extra_datas[call.from_user.id]["day_id"] = int(call.data.split("|")[2])
#     weekday = DocWorkDay.objects.filter(
#         pk=extra_datas[call.from_user.id]["day_id"]
#     ).first()
#     markup = types.InlineKeyboardMarkup(row_width=2)

#     back = types.InlineKeyboardButton("🛑Bekor qilish", callback_data="back")
#     markup.add(back)
#     bot.delete_message(call.from_user.id, message_id=call.message.message_id)
#     time = Time.objects.filter(id=extra_datas[call.from_user.id]["time_id"])[0]

#     patient = Patient.objects.filter(user_id=call.from_user.id)[0]
#     app = Appointment.objects.create(
#         patient=patient, docworkday=weekday, time=time, type="bot"
#     )
#     bot.send_message(
#         CHANNEL,
#         f"<b>Shifokor qabuliga yozilgan be'mor ma'lumotlari:\nAriza tartib raqami: <i>{app.id}</i>\nIsmi: <i>{patient.first_name}</i>\nFamiliyasi: <i>{patient.last_name}</i>\n{f'Telegram: @{patient.username}' if patient.username else ''}\nMas'ul shifokor: <i>{weekday.doctor.first_name}</i>\nQabul kuni: <i>{weekday.day.week_day}</i>\nQabul vaqti: <i>{time.start_time.strftime('%H:%M')}</i></b>",
#     )
#     text = f"<b>Siz <i>{weekday.day.week_day}</i> kuni\nSoat <i>{time.start_time.strftime('%H:%M')}</i> da \nDoktor <i>{weekday.doctor.first_name}</i> qabuliga ro`yhatga olindingiz</b>"
#     markup = types.ReplyKeyboardMarkup(
#         row_width=2, resize_keyboard=True, one_time_keyboard=True
#     )
#     btn = types.KeyboardButton(str(_("Qabulga yozilish")))
#     btn1 = types.KeyboardButton(str(_("Qabulni ko`rish")))
#     btn2 = types.KeyboardButton(str(_("Tezkor Aloqa")))
#     markup.add(btn, btn2, btn1)
#     bot.send_message(call.from_user.id, text, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "en" or call.data == "ru")
def latin(call):
    user = Patient.objects.get(user_id=call.from_user.id)
    user.language = call.data
    user.save()
    activate(user.language)
    text = str(
        _(
            f"<b>Assalomu alaykum <i>{call.from_user.first_name}</i>.\nBizning xizmatlardan foydalanish uchun avval ro`yhatdan o`ting!</b>"
        )
    )
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn = types.KeyboardButton(str(_("Ro`yhatdan o`tish")))
    markup.add(btn)
    bot.delete_message(call.from_user.id, call.message.message_id)
    bot.send_message(call.from_user.id, text, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "back")
def back(call):
    bot.delete_message(call.from_user.id, call.message.message_id)
    markup = types.ReplyKeyboardMarkup(
        row_width=2, resize_keyboard=True, one_time_keyboard=True
    )
    btn = types.KeyboardButton(str(_("Qabulga yozilish")))
    btn1 = types.KeyboardButton(str(_("Tezkor Aloqa")))
    btn3 = types.KeyboardButton(str(_("Profil")))
    markup.add(btn, btn1)
    if Appointment.objects.filter(patient__user_id=call.from_user.id, active=True):
        btn4 = types.KeyboardButton(str(_("Qabulni ko`rish")))
        markup.add(btn4)
    markup.add(btn3)
    bot.send_message(call.from_user.id, "<b>Bosh menu</b>", reply_markup=markup)


def send_process(message):
    if message.text == "🛑Bekor qilish":
        Letter.objects.filter(active=True, admin_id=message.from_user.id).delete()
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        btn = types.KeyboardButton("Button")
        markup.add(btn)
        bot.send_message(
            message.from_user.id, "Habar yuborish bekor qilindi!", reply_markup=markup
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
            btn = types.KeyboardButton("Button")
            markup.add(btn)
            us = len(Patient.objects.all())
            total = letter.count
            bot.send_message(
                int(ADMIN),
                f"<b><u>Habar yuborishda yakunlandi:</u></b>\n<b>Jami foydalanuvchilar soni:</b> {us}\n<b>Muvafaqqiyatli yuborilgan habar soni:</b> {total}\n<b>Muvafaqqiyatsiz yuborilgan habar soni:</b> {us - total}",
                reply_markup=markup,
            )
            letter.active = False
            letter.save()
            response = HttpResponse()
            response.write("<h1>Habar yuborilishi muvofaqqiyatli yakunlandi!</h1>")
            return response

        response = HttpResponse()
        response.write("<h1>Habar yuborilmoqda!</h1>")
        return response
