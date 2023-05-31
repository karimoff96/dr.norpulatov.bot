from django.shortcuts import render
from telebot import types
import telebot
from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Patient, Appointment, Doctor, DocWorkDay, WeekDay, Time
from django.utils.translation import gettext_lazy as _
from environs import Env
from django.utils.translation import activate
from telebot.apihelper import ApiTelegramException

# Create your views here.
env = Env()
env.read_env()

CHANNEL = env.int("CHANNEL")
bot = telebot.TeleBot(env.str("BOT_TOKEN"), parse_mode="HTML")
SHIKOYAT_MATNI = ""

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
    for app in apps:
        if app.urgent == True:
            text = str(
                _(
                    f"<u><b>‼️Tezkor qabul.\nFoydalanuvchi ma`lumotlari:</b></u>\n<b>Tartib raqami:</b>  {app.id}\n<b>Ismi:</b>  {app.patient.first_name}\n<b>Telefon raqam:</b>  {app.patient.phone_number}"
                )
            )
        else:
            text = str(
                _(
                    f"<u><b>Foydalanuvchi ma`lumotlari:</b></u>\n<b>Tartib raqami:</b>  {app.id}\n<b>Ismi:</b>  {app.patient.first_name}\n<b>Familyasi:</b>  {app.patient.last_name}\n<b>Telefon raqam:</b> {app.patient.phone_number}\n<b>Shikoyat bayoni:</b>  {app.complaint}\n"
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
    markup.add(btn, btn1)
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
    global SHIKOYAT_MATNI
    SHIKOYAT_MATNI = message.text
    bot_user = Patient.objects.get(user_id=message.from_user.id)
    bot_user.step=200
    activate(bot_user.language)
    bot_user.save()
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn2 = types.KeyboardButton(str(_("🛑Bekor qilish")))
    markup.add(btn2)
    bot.send_message(message.from_user.id, str(_("Shikoyat matnini kiriting:")), reply_markup=markup)
    


@bot.message_handler(
    func=lambda message: message.text == str(_("Shikoyatni o`zgartirish"))
)
def change_complaint(message):
    global SHIKOYAT_MATNI
    SHIKOYAT_MATNI = message.text
    bot_user = Patient.objects.get(user_id=message.from_user.id)
    activate(bot_user.language)
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn = types.KeyboardButton(str(_("Tasdiqlash")))
    btn1 = types.KeyboardButton(str(_("Shikoyatni o`zgartirish")))
    btn2 = types.KeyboardButton(str(_("🛑Bekor qilish")))
    markup.add(btn, btn1, btn2)
    text = str(
        _(
            f"Tezkor ko`rik uchun ariza topshiruvchi be`mor ma`lumotlari:\nIsmi: {bot_user.first_name}\nFamilyasi: {bot_user.last_name}\nTelefon raqami: {bot_user.phone_number}\nShikoyati: Tezkor aloqa!{SHIKOYAT_MATNI}\n\nBarcha ma`lumotlaringiz to`gri bo`lsa tasdiqlash tugmasini bosing!"
        )
    )
    bot.send_message(message.from_user.id, text, reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == str(_("Tasdiqlash")))
def confirm(message):
    bot_user = Patient.objects.filter(user_id=message.from_user.id)
    Appointment.objects.create(
        patient=bot_user[0], complaint=SHIKOYAT_MATNI, urgetn=True
    )
    apps = Appointment.objects.filter(patient=bot_user)
    activate(bot_user.language)
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
        str(_("<b>Shifokor qabuliga yozilish</b>")),
        reply_markup=markup,
    )


@bot.message_handler(func=lambda message: message.text == str(_("Qabulga yozilish")))
def make_appointment(message):
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
        str(_("Shiforkorni tanlang: Shifokor haqida ma`lumot....")),
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
    elif bot_user.step == 100:
        Appointment.objects.create(
            patient=bot_user[0], complaint=message.text, urgent=True
        )
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        text = str(
            _(
                f"Tezkor ko`rik uchun ariza topshiruvchi be`mor ma`lumotlari:\nIsmi: {bot_user.first_name}\nFamilyasi: {bot_user.last_name}\nTelefon raqami: {bot_user.phone_number}\nQo`shimcha ma`lumot: Tezkor aloqa! {message.text}"
            )
        )
        bot.send_message(
            message.chat.id,
            str(
                _(
                    "Tezkor arizangiz adminlarga yuborildi va tez orada hodimlarimiz siz bilan bog`lanishadi."
                )
            ),
            reply_markup=markup,
        )
    elif bot_user.step==200 and len(message.text)>0:
        

@bot.message_handler(content_types=["contact"])
def contact(message):
    bot_user = Patient.objects.get(user_id=message.from_user.id)
    activate(bot_user.language)

    if message.contact is not None and message.contact.phone_number:
        phone_number = message.contact.phone_number
        bot_user.phone_number = phone_number
        # if bot_user.step == 101:
        #     markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        #     btn = types.KeyboardButton(str(_("Qabulga yozilish")))
        #     btn1 = types.KeyboardButton(str(_("Qabulni ko`rish")))
        #     btn2 = types.KeyboardButton(str(_("Tezkor Aloqa")))
        #     markup.add(btn, btn1, btn2)
        #     Appointment.objects.create(patient=bot_user, urgent=True)
        #     apps = Appointment.objects.filter(patient=bot_user).last()
        #     if len(message.from_user.username) > 0:
        #         text = str(
        #             _(
        #                 f"<u><b>‼️Tezkor qabul.\nFoydalanuvchi ma`lumotlari:</b></u>\n<b>Tartib raqami:</b>  {apps.id}\n<b>Ismi:</b>  {apps.patient.first_name}\n<b>Profil:</b>  @{apps.patient.username}\n<b>Telefon raqam:</b>  {apps.patient.phone_number}"
        #             )
        #         )
        #     else:
        #         text = str(
        #             _(
        #                 f"<u><b>‼️Tezkor qabul.\nFoydalanuvchi ma`lumotlari:</b></u>\n<b>Tartib raqami:</b>  {apps.id}\n<b>Ismi:</b>  {apps.patient.first_name}\n<b>Telefon raqam:</b>  {apps.patient.phone_number}"
        #             )
        #         )
        #     bot.send_message(CHANNEL, text)
        #     bot.send_message(
        #         message.from_user.id,
        #         str(
        #             _(
        #                 "Habaringiz adminga yuborildi. Siz bilan tez orada bog`lanishadi!"
        #             )
        #         ),
        #         reply_markup=markup,
        #     )

        # else:
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
    doc_id = call.data.split("|")[1]
    docworkdays = DocWorkDay.objects.filter(doctor__pk=doc_id)
    markup = types.InlineKeyboardMarkup(row_width=2)
    row_buttons = []
    for docworkday in docworkdays:
        button = types.InlineKeyboardButton(
            docworkday.day.week_day, callback_data=f"day|{docworkday.id}"
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
    bot.send_message(call.from_user.id, "Hafta kunini tanlang", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("day|"))
def handle_callback_query(call):
    print("day")
    day_id = call.data.split("|")[1]
    weekday = DocWorkDay.objects.filter(pk=day_id).first()
    times: list[Time] = weekday.times.all()
    markup = types.InlineKeyboardMarkup(row_width=2)
    row_buttons = []
    for time in times:
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
        call.from_user.id, "Mavjud vaqtlardan birini tanlang", reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("time|"))
def handle_callback_query(call):
    time_id = call.data.split("|")[1]
    day_id = call.data.split("|")[2]
    weekday = DocWorkDay.objects.filter(pk=day_id).first()
    times: list[Time] = weekday.times.all()
    markup = types.InlineKeyboardMarkup(row_width=2)
    row_buttons = []
    for time in times:
        button = types.InlineKeyboardButton(
            time.start_time.strftime("%H:%M"), callback_data=f"time|{time.id}{day_id}"
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
    patient = Patient.objects.filter(user_id=call.from_user.id)[0]
    time = Time.objects.filter(id=time_id)[0]
    Appointment.objects.create(patient=patient, docworkday=weekday, time=time)
    text = f"Siz {weekday.day.week_day} kuni\n soat {time} da \ndoktor {weekday.doctor.first_name} qabuliga ro`yhatga olindingiz"
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
            f"<i>Assalomu alaykum {call.from_user.first_name}.\n<b>Bizning xizmatlardan foydalanish uchun avval ro`yhatdan o`ting!</b></i>"
        )
    )
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn = types.KeyboardButton(str(_("Ro`yhatdan o`tish")))
    # btn1 = types.KeyboardButton(str(_("Tezkor Aloqa")))
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
    bot.send_message(call.from_user.id, "Bosh menu", reply_markup=markup)


def cron_job(request):
    users = Patient.objects.filter(active=False)
    fail = 0
    success = 0
    for u in users:
        try:
            bot.send_message(
                u.user_id,
                "Hurmatli foydalanuvchi botdan to`liq ro`yhatdan o`tmaganingizcha biz siz haqingizda ma`limotga ega bo`la olmaymiz.\nIltimos qabulga yozilishni yakunlang!",
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
        f'To`liq ro`yhatdan o`tmagan foydalanuvchilarga "Registrtatsiyani yakunlash" to`grisidagi eslatma habar yuborish yakunlandi!\nNofaol foydalanuvchilar: {success}\nBotni blocklagan foydalanuvchilar: {fail}',
    )
    return response
