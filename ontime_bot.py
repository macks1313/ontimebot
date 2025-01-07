from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import re

# Data storage for work hours
data = {}

def start(update: Update, context: CallbackContext):
    user_name = update.message.from_user.first_name
    update.message.reply_text(
        f"Salut {user_name} ! Prêt à découvrir combien d'heures de ta vie tu sacrifies au travail ? \n"
        "Voici les commandes que tu peux utiliser : \n"
        "/h <début> <fin> <pause> : Ajoute tes heures (format : /h 8h45 19h30 30).\n"
        "/reset : Réinitialise tes heures cumulées.\n"
        "/total : Affiche le total des heures travaillées depuis la dernière réinitialisation.\n"
        "/info : Affiche ce récapitulatif.\n"
        "Je promets d'être sarcastique mais honnête \ud83d\ude09"
    )

def calculate_hours(start: str, end: str, break_minutes: int):
    start_hours, start_minutes = map(int, start.split('h'))
    end_hours, end_minutes = map(int, end.split('h'))

    start_total_minutes = start_hours * 60 + start_minutes
    end_total_minutes = end_hours * 60 + end_minutes

    total_work_minutes = end_total_minutes - start_total_minutes - break_minutes
    work_hours = total_work_minutes // 60
    work_minutes = total_work_minutes % 60

    return work_hours, work_minutes

def handle_hours(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name
    text = " ".join(context.args)

    match = re.match(r"(\d+h\d+)\s+(\d+h\d+)\s+(\d+)", text)
    if not match:
        update.message.reply_text(
            f"Euh {user_name}... Essaie encore ? Format attendu : /h 8h45 19h30 30. T'inquiète, on est tous un peu perdus parfois."
        )
        return

    start_time, end_time, break_minutes = match.groups()
    work_hours, work_minutes = calculate_hours(start_time, end_time, int(break_minutes))

    if user_id not in data:
        data[user_id] = 0

    total_minutes = work_hours * 60 + work_minutes
    data[user_id] += total_minutes

    update.message.reply_text(
        f"Bravo {user_name} ! Aujourd'hui, tu as travaillé {work_hours}h et {work_minutes}min. \ud83d\udcbc\n"
        f"Au total, tu es à {data[user_id] // 60}h et {data[user_id] % 60}min. Allez, continue de faire tourner l'économie ! \ud83d\ude44"
    )

def reset_data(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name
    if user_id in data:
        del data[user_id]
        update.message.reply_text(f"Hop {user_name} ! Tes heures de travail ont été effacées. Profites-en pour prétendre que tu es libre. \ud83c\udf08")
    else:
        update.message.reply_text(f"Hum {user_name}... Je n'ai rien à effacer. Peut-être que tu n'as pas autant travaillé que tu pensais ? \ud83d\ude02")

def total_hours(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name
    if user_id in data:
        total_minutes = data[user_id]
        update.message.reply_text(
            f"Depuis la dernière réinitialisation, tu as accumulé {total_minutes // 60}h et {total_minutes % 60}min. Impressionnant, non {user_name} ? \ud83e\udd13"
        )
    else:
        update.message.reply_text(f"Aucun temps de travail enregistré pour l'instant, {user_name}. Prends un café et reviens plus tard ! ☕")

def info(update: Update, context: CallbackContext):
    user_name = update.message.from_user.first_name
    update.message.reply_text(
        f"Voici les commandes disponibles pour toi, {user_name} : \n"
        "/h <début> <fin> <pause> : Ajoute tes heures (format : /h 8h45 19h30 30).\n"
        "/reset : Réinitialise tes heures cumulées.\n"
        "/total : Affiche le total des heures travaillées depuis la dernière réinitialisation.\n"
        "/info : Affiche ce récapitulatif.\n"
        "Et souviens-toi, je suis là pour t'aider... avec un peu de sarcasme. \ud83d\ude09"
    )

def main():
    bot_token = "7685304448:AAEuMefo6gvKOydyTtRv6pVXLMxvTuJfWr4"
    updater = Updater(bot_token)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("h", handle_hours))
    dp.add_handler(CommandHandler("reset", reset_data))
    dp.add_handler(CommandHandler("total", total_hours))
    dp.add_handler(CommandHandler("info", info))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
