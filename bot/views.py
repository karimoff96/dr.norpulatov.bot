import telebot
from django.shortcuts import HttpResponse
from django.utils.translation import activate
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from environs import Env
from telebot import types
from telebot.apihelper import ApiTelegramException

from .models import Appointment, Doctor, DocWorkDay, Patient, Time

# Create your views here.
env = Env()
env.read_env()

CHANNEL = env.int("CHANNEL")
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


@bot.message_handler(commands=["start"])
def start(message):
    if Patient.objects.filter(active=True):
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
        Patient.objects.create(
            user_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
        )
        text = "Tinlni tanlang\nТинлни танланг"
        markup = types.InlineKeyboardMarkup(row_width=2)
        b = types.InlineKeyboardButton("Lotin", callback_data="en")
        b1 = types.InlineKeyboardButton("Кирилл", callback_data="ru")
        markup.add(b, b1)
        bot.send_message(message.chat.id, text, reply_markup=markup)


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
        markup.add(btn, btn1)
        if len(app) > 0:
            btn2 = types.KeyboardButton(str(_("Qabulni ko`rish")))
            markup.add(btn2)

        bot.send_message(
            message.chat.id,
            str(_("<b>Shifokor qabuliga yozilish</b>")),
            reply_markup=markup,
        )


@bot.message_handler(func=lambda message: message.text == str(_("Qabulni ko`rish")))
def checkout(message):
    markup = types.ReplyKeyboardMarkup(
        row_width=2, resize_keyboard=True, one_time_keyboard=True
    )
    btn = types.KeyboardButton(str(_("Qabulga yozilish")))
    btn1 = types.KeyboardButton(str(_("Qabulni ko`rish")))
    btn2 = types.KeyboardButton(str(_("Tezkor Aloqa")))
    markup.add(btn, btn2, btn1)
    bot_user = Patient.objects.get(user_id=message.from_user.id)
    activate(bot_user.language)
    apps = Appointment.objects.filter(patient=bot_user)
    bot.send_message(message.from_user.id, '<b><u>Sizning arizalaringiz</u></b>', reply_markup=markup)
    for app in apps:
        if app.urgent == True:
            text = str(
                _(
                    f"<u><b>‼️Tezkor qabul arizasi.</b></u>\n<b>Tartib raqami:</b>  {app.id}\n<b>Ismi:</b>  <i>{app.patient.first_name}</i>\n<b>Telefon raqam:</b>  <i>{app.patient.phone_number}</i>\n<b>Shikoyat matni:</b> <i>Tezkor aloqa! {app.complaint}</i>\n<b>Yaratilgan vaqti:</b> <i>{app.created}</i>"
                )
            )
        else:
            text = str(
                _(
                    f"<b>Tartib raqami:</b>  <i>{app.id}</i>\n<b>Ism:</b>  <i>{app.patient.first_name}</i>\n<b>Familya:</b>  <i>{app.patient.last_name}</i>\n<b>Telefon raqam:</b> <i>{app.patient.phone_number}</i>\n<b>Mas'ul shifokor:</b> <i>{app.docworkday.doctor}</i>\n<b>Qabul kuni:</b> <i>{app.docworkday.day.week_day}</i>\n<b>Qabul vaqti:</> <i>{app.time}</i>\n<b>Yaratilgan vaqti:</b> <i>{app.created}</i>"
                )
            )
        bot.send_message(message.from_user.id, text, reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == str(_("Ro`yhatdan o`tish")))
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
            f"Tezkor ko`rik uchun ariza topshiruvchi be`mor ma`lumotlari:\nIsmi: {bot_user.first_name}\nFamilyasi: {bot_user.last_name}\nTelefon raqami: {bot_user.phone_number}\nShikoyati: Tezkor aloqa!\n\nBarcha ma`lumotlaringiz to`gri bo`lsa tasdiqlash tugmasini bosing!\nP.S: Shikoyat matnini kiritish ixtiyori!"
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
        message.from_user.id, str(_("Shikoyat matnini kiriting:")), reply_markup=markup
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
            f"Tezkor ko`rik uchun ariza topshiruvchi be`mor ma`lumotlari:\nIsmi: {bot_user.first_name}\nFamilyasi: {bot_user.last_name}\nTelefon raqami: {bot_user.phone_number}\nShikoyati: Tezkor aloqa!{message.text}\n\nBarcha ma`lumotlaringiz to`gri bo`lsa tasdiqlash tugmasini bosing!"
        )
    )
    bot.send_message(message.from_user.id, text, reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == str(_("Tasdiqlash")))
def confirm(message):
    global extra_datas
    patient = Patient.objects.filter(user_id=message.from_user.id)[0]
    Appointment.objects.create(
        patient=patient,
        complaint=extra_datas[message.from_user.id]["complaint"],
        urgent=True,
    )

    apps = Appointment.objects.filter(patient=patient)
    activate(patient.language)
    markup = types.ReplyKeyboardMarkup(
        row_width=2, resize_keyboard=True, one_time_keyboard=True
    )
    btn = types.KeyboardButton(str(_("Qabulga yozilish")))
    btn1 = types.KeyboardButton(str(_("Tezkor Aloqa")))
    markup.add(btn, btn1)
    if len(apps) > 0:
        btn2 = types.KeyboardButton(str(_("Qabulni ko`rish")))
        markup.add(btn2)
    bot.send_message(
        message.chat.id,
        str(
            _(
                "Tezkor arizangiz adminlarga yuborildi va tez orada hodimlarimiz siz bilan bog`lanishadi."
            )
        ),
        reply_markup=markup,
    )
    bot.send_message(
        message.chat.id,
        str(_("<b>Shifokor qabuliga yozilish</b>")),
        reply_markup=markup,
    )


@bot.message_handler(func=lambda message: message.text == str(_("Qabulga yozilish")))
def make_appointment(message):
    global extra_datas
    extra_datas[message.from_user.id] = {}
    bot_user = Patient.objects.get(user_id=message.from_user.id)
    activate(bot_user.language)
    doctors = Doctor.objects.filter(active=True)
    markup = types.InlineKeyboardMarkup(row_width=2)
    row_buttons = []
    for doc in doctors:
        button = types.InlineKeyboardButton(
            doc.first_name, callback_data=f"doctor|{doc.id}"
        )
        row_buttons.append(button)
        if len(row_buttons) == 2:
            markup.add(*row_buttons)
            row_buttons = []

    if len(row_buttons) == 1:
        markup.add(row_buttons[0])

    back = types.InlineKeyboardButton("🛑Bekor qilish", callback_data="back")
    markup.add(back)

    bot.send_message(
        message.chat.id,
        str(_("Bu yerga Shifoxona yoki servis xizmat yurlari haqida qisqacha malumot yozilishi mumkin")),
        reply_markup=markup,
    )


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
        markup.add(btn, btn2)
        bot.send_message(
            message.chat.id, str(_(f"Telefon raqam qabul qilindi: {phone_number}"))
        )
        bot.send_message(
            message.chat.id,
            str(_("Ro`yhatdan o`tish muvaffaqqiyatli yakunlandi!")),
            reply_markup=markup,
        )


@bot.callback_query_handler(func=lambda call: call.data.startswith("doctor|"))
def handle_callback_query(call):
    global extra_datas
    doc_id = call.data.split("|")[1]
    extra_datas[call.from_user.id]["doctor_id"] = doc_id
    docworkdays = DocWorkDay.objects.filter(doctor__pk=doc_id)
    markup = types.InlineKeyboardMarkup(row_width=2)
    row_buttons = []
    for docworkday in docworkdays:
        times = docworkday.times.all()
        for time in times:
            if not Appointment.objects.filter(docworkday=docworkday, time=time).exists():
                button = types.InlineKeyboardButton(
                    docworkday.day.week_day, callback_data=f"day|{docworkday.id}"
                )
                row_buttons.append(button)
                if len(row_buttons) == 2:
                    markup.add(*row_buttons)
                break
    if len(row_buttons) == 1:
        markup.add(row_buttons[0])
        print(*row_buttons)
    elif len(row_buttons)== 0:
        text = '<i>Shifokorning qabul qilish vaqtlari mavjud emas</i>'
    else:
        print(3)
        text = f"<i>{Doctor.objects.get(id=doc_id).about}</i>"
    back = types.InlineKeyboardButton("🛑Bekor qilish", callback_data="back")
    markup.add(back)
    bot.delete_message(call.from_user.id, message_id=call.message.message_id)
    bot.send_message(
        call.from_user.id, text, reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("day|"))
def handle_callback_query(call):
    day_id = call.data.split("|")[1]
    weekday = DocWorkDay.objects.filter(pk=day_id).first()
    times: list[Time] = weekday.times.all()
    markup = types.InlineKeyboardMarkup(row_width=2)
    row_buttons = []
    for time in times:
        if Appointment.objects.filter(docworkday_id=day_id, time=time).exists():
            continue
        button = types.InlineKeyboardButton(
            time.start_time.strftime("%H:%M"), callback_data=f"time|{time.id}|{day_id}"
        )
        row_buttons.append(button)
        if len(row_buttons) == 2:
            markup.add(*row_buttons)
            row_buttons = []
    if len(row_buttons) == 1:
        markup.add(row_buttons[0])
    back = types.InlineKeyboardButton("🛑Bekor qilish", callback_data="back")
    markup.add(back)
    bot.delete_message(call.from_user.id, message_id=call.message.message_id)

    bot.send_message(
        call.from_user.id,
        "<i>Mavjud vaqtlardan birini tanlang</i>",
        reply_markup=markup,
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("time|"))
def handle_callback_query(call):
    global extra_datas
    extra_datas[call.from_user.id]["time_id"] = call.data.split("|")[1]
    extra_datas[call.from_user.id]["day_id"] = int(call.data.split("|")[2])
    weekday = DocWorkDay.objects.filter(
        pk=extra_datas[call.from_user.id]["day_id"]
    ).first()
    markup = types.InlineKeyboardMarkup(row_width=2)

    back = types.InlineKeyboardButton("🛑Bekor qilish", callback_data="back")
    markup.add(back)
    bot.delete_message(call.from_user.id, message_id=call.message.message_id)
    time = Time.objects.filter(id=extra_datas[call.from_user.id]["time_id"])[0]

    patient = Patient.objects.filter(user_id=call.from_user.id)[0]

    app=Appointment.objects.create(patient=patient, docworkday=weekday, time=time)
    bot.send_message(CHANNEL, f"<b>Shifokor qabuliga yozilgan be'mor ma'lumotlari:\nAriza tartib raqami: <i>{app.id}</i>\nIsmi: <i>{patient.first_name}</i>\nFamiliyasi: <i>{patient.last_name}</i>\n{'Telegram: {patient.username}' if patient.username else ''}Mas'ul shifokor: <i>{weekday.doctor.first_name}</i>\nQabul kuni: <i>{weekday.day.week_day}</i>\nQabul vaqti: <i>{time}</i></b>")
    text = f"<b>Siz <i>{weekday.day.week_day}</i> kuni\nSoat <i>{time}</i> da \nDoktor <i>{weekday.doctor.first_name}</i> qabuliga ro`yhatga olindingiz</b>"
    markup = types.ReplyKeyboardMarkup(
        row_width=2, resize_keyboard=True, one_time_keyboard=True
    )
    btn = types.KeyboardButton(str(_("Qabulga yozilish")))
    btn1 = types.KeyboardButton(str(_("Qabulni ko`rish")))
    btn2 = types.KeyboardButton(str(_("Tezkor Aloqa")))
    markup.add(btn, btn2, btn1)
    bot.send_message(call.from_user.id, text, reply_markup=markup)


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
    bot.send_message(call.from_user.id, text, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "back")
def back(call):
    bot.delete_message(call.from_user.id, call.message.message_id)
    markup = types.ReplyKeyboardMarkup(
        row_width=2, resize_keyboard=True, one_time_keyboard=True
    )
    btn = types.KeyboardButton(str(_("Qabulga yozilish")))
    btn2 = types.KeyboardButton(str(_("Tezkor Aloqa")))
    markup.add(btn, btn2)
    if Appointment.objects.filter(patient__user_id=call.from_user.id):
        btn1 = types.KeyboardButton(str(_("Qabulni ko`rish")))
        markup.add(btn1)
    bot.send_message(call.from_user.id, "<b>Bosh menu</b>", reply_markup=markup)


def cron_job(request):
    users = Patient.objects.filter(active=False)
    fail = 0
    success = 0
    for u in users:
        try:
            bot.send_message(
                u.user_id,
                "<b>Hurmatli foydalanuvchi botdan to`liq ro`yhatdan o`tmaganingizcha biz siz haqingizda ma`limotga ega bo`la olmaymiz.\nIltimos qabulga yozilishni yakunlang!</b>",
            )
            success += 1
        except ApiTelegramException:
            fail += 1
    response = HttpResponse()
    response.write(
        f"<h1>Habar yuborishda yakunlandi: </h1>\nSuccess: {success}\nFail: {fail}"
    )
    bot.send_message(
        CHANNEL,
        f'<b>To`liq ro`yhatdan o`tmagan foydalanuvchilarga "Registrtatsiyani yakunlash" to`grisidagi eslatma habar yuborish yakunlandi!</b>\n<b>Nofaol foydalanuvchilar:</b> <i>{success}</i>\n<b>Botni blocklagan foydalanuvchilar:</b> <i>{fail}</i>',
    )
    return response
