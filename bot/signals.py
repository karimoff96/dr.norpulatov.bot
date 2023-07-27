import requests
from django.shortcuts import HttpResponse
from environs import Env
from telebot.apihelper import ApiTelegramException

from .models import Appointment, Patient

env = Env()
env.read_env()
CHANNEL = env.int("CHANNEL")


def send_appointment_to_doctor(message: dict, to: str = "well_admin"):
    text = f"""Yangi qabul!\nTartib raqami: {message['id']}\nBe'mor ismi: {message['patient']['first_name']}\nBe'mor familiyasi: {message['patient']['last_name']}\nQabul kuni: {message['appointment']['day']}\nQabul soati: {message['appointment']['time']}\nYaratilgan vaqti: {message['appointment']['created_at']}\n{f'Qo`shimcha: {message["patient"]["complaint"]}' if len(message['patient']['complaint'])>0 else 'Qo`shimcha: Admin panel orqali ariza yaratildi'} """
    print(text)
    url = f"""https://api.telegram.org/bot{env.str("BOT_TOKEN")}/sendMessage?chat_id={to}&text={text}"""
    try:
        _ = requests.get(url)
    except:
        pass


def cron_job(request):
    users = Patient.objects.filter(active=False)
    fail = 0
    success = 0
    for_users = "Hurmatli foydalanuvchi botdan to`liq ro`yhatdan o`tmaganingizcha biz siz haqingizda ma`limotga ega bo`la olmaymiz.\nIltimos qabulga yozilishni yakunlang!"
    for u in users:
        url = f"""https://api.telegram.org/bot{env.str("BOT_TOKEN")}/sendMessage?chat_id={u.user_id}&text={for_users}"""
        try:
            _ = requests.get(url)
            success += 1
        except ApiTelegramException:
            fail += 1
    response = HttpResponse()
    response.write(
        f"<h1>Habar yuborishda yakunlandi: </h1>\nSuccess: {success}\nFail: {fail}"
    )
    for_channel = f"To`liq ro`yhatdan o`tmagan foydalanuvchilarga 'Registrtatsiyani yakunlash' to`grisidagi eslatma habar yuborish yakunlandi!\nNofaol foydalanuvchilar: {success}\nBotni blocklagan foydalanuvchilar: {fail}"
    url = f"""https://api.telegram.org/bot{env.str("BOT_TOKEN")}/sendMessage?chat_id={CHANNEL}&text={for_channel}"""
    return response


def clear_appointment(request):
    appointments = Appointment.objects.all()

    for app in appointments:
        if app.urgent == False:
            app.active = False
            app.save()
    return
