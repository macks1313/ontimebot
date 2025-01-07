from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext
import re

# Data storage for work hours
data = {}

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Salut ! Je suis votre bot assistant de calcul d'heures de travail. Utilisez /h pour ajouter des heures, et d'autres commandes sympas sont en route ! \ud83d\ude80"
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
    text = " ".join(context.args)

    match = re.match(r"(\d+h\d+)\s+(\d+h\d+)\s+(\d+)", text)
    if not match:
        update.message.reply_text("Oups ! Format incorrect. Utilisez : /h 8h45 19h30 25")
        return

    start_time, end_time, break_minutes = match.groups()
    work_hours, work_minutes = calculate_hours(start_time, end_time, int(break_minutes))

    if user_id not in data:
        data[user_id] = 0

    total_minutes = work_hours * 60 + work_minutes
    data[user_id] += total_minutes

    update.message.reply_text(
        f"Vous avez travaillé {work_hours} heures et {work_minutes} minutes aujourd'hui \ud83d\udcbc. \n"
        f"Total cumulé : {data[user_id] // 60} heures et {data[user_id] % 60} minutes. \ud83d\udcc8"
    )

def reset_data(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id in data:
        del data[user_id]
        update.message.reply_text("Toutes vos données ont été supprimées. C'est reparti de zéro ! \ud83d\udeaa")
    else:
        update.message.reply_text("Pas de données à supprimer pour le moment. Profitez de votre temps libre ! \ud83c\udf89")

def joke(update: Update, context: CallbackContext):
    update.message.reply_text("Pourquoi les développeurs aiment-ils le café ? Parce qu'ils aiment le code java ! \ud83d\ude09")

def motivation(update: Update, context: CallbackContext):
    update.message.reply_text("N'oubliez pas : chaque minute compte ! \ud83c\udfc6 \nGagnez la journée, une heure à la fois. \u2728")

def main():
    bot_token = "7685304448:AAEuMefo6gvKOydyTtRv6pVXLMxvTuJfWr4"
    updater = Updater(bot_token)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("h", handle_hours))
    dp.add_handler(CommandHandler("reset", reset_data))
    dp.add_handler(CommandHandler("joke", joke))
    dp.add_handler(CommandHandler("motivation", motivation))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
