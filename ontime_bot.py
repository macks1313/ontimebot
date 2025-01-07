from telegram import 
Update from telegram.ext import Application, CommandHandler, ContextTypes
from datetime import datetime, timedelta
import re
import pdfkit

# Token du bot Telegram fourni par BotFather
TOKEN = "7685304448:AAEuMefo6gvKOydyTtRv6pVXLMxvTuJfWr4"

# Dictionnaire pour stocker les données utilisateur
user_data = {}

# Langues disponibles
LANGUAGES = {
    "fr": {
        "welcome": "Bienvenue sur OnTime Bot ! \n\nVoici les commandes disponibles : \n\n/add arrivée départ - Ajouter une session de travail\n/recap - Voir votre total d'heures travaillées\n/reset - Réinitialiser vos données\n/export - Exporter les données en PDF",
        "no_sessions": "Aucune session enregistrée. Essayez /add pour commencer !",
        "invalid_time_format": "Format d'heure invalide. Utilisez HH:MM ou HHhMM.",
        "session_saved": "Session enregistrée avec succès !",
        "data_reset": "Données réinitialisées avec succès !",
        "export_failure": "Erreur lors de l'exportation des données en PDF."
    },
    "en": {
        "welcome": "Welcome to OnTime Bot! \n\nHere are the available commands: \n\n/add start end - Add a work session\n/recap - View your total work hours\n/reset - Reset your data\n/export - Export data to PDF",
        "no_sessions": "No sessions recorded. Try /add to start!",
        "invalid_time_format": "Invalid time format. Use HH:MM or HHhMM.",
        "session_saved": "Session successfully saved!",
        "data_reset": "Data successfully reset!",
        "export_failure": "Error occurred while exporting data to PDF."
    },
    "uk": {
        "welcome": "Ласкаво просимо до OnTime Bot! \n\nОсь доступні команди: \n\n/add прибуття відбуття - Додати сесію роботи\n/recap - Переглянути загальний час роботи\n/reset - Скинути дані\n/export - Експортувати дані у PDF",
        "no_sessions": "Сесій не зареєстровано. Спробуйте /add, щоб розпочати!",
        "invalid_time_format": "Неправильний формат часу. Використовуйте HH:MM або HHhMM.",
        "session_saved": "Сесію успішно збережено!",
        "data_reset": "Дані успішно скинуто!",
        "export_failure": "Сталася помилка під час експорту даних у PDF."
    }
}

# Fonction pour détecter la langue de l'utilisateur
def get_language(user_id):
    # Par défaut, on retourne le français
    return "fr"

# Fonction pour analyser l'heure
def parse_time(time_str):
    try:
        time_str = time_str.replace("h", ":").lower()
        if "am" in time_str or "pm" in time_str:
            return datetime.strptime(time_str, "%I:%M%p").time()
        else:
            return datetime.strptime(time_str, "%H:%M").time()
    except ValueError:
        raise ValueError("Invalid time format")

# Commande /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_language(update.message.from_user.id)
    await update.message.reply_text(LANGUAGES[lang]["welcome"])

# Commande /add
async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    lang = get_language(user_id)

    if len(context.args) != 2:
        await update.message.reply_text(LANGUAGES[lang]["invalid_time_format"])
        return

    try:
        arrive_time = parse_time(context.args[0])
        depart_time = parse_time(context.args[1])

        arrive_datetime = datetime.combine(datetime.today(), arrive_time)
        depart_datetime = datetime.combine(datetime.today(), depart_time)

        if depart_datetime <= arrive_datetime:
            await update.message.reply_text(LANGUAGES[lang]["invalid_time_format"])
            return

        worked_time = depart_datetime - arrive_datetime

        if user_id not in user_data:
            user_data[user_id] = {"sessions": [], "total_time": timedelta()}

        user_data[user_id]["sessions"].append((arrive_time, depart_time, worked_time))
        user_data[user_id]["total_time"] += worked_time

        await update.message.reply_text(LANGUAGES[lang]["session_saved"])

    except ValueError:
        await update.message.reply_text(LANGUAGES[lang]["invalid_time_format"])

>>>>>>> bdc21e8 (Fix missing import for Update)
# Commande /recap
async def recap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    lang = get_language(user_id)

    if user_id in user_data and user_data[user_id]["sessions"]:
        total_time = user_data[user_id]["total_time"]
        hours, remainder = divmod(total_time.total_seconds(), 3600)
        minutes = remainder // 60
        await update.message.reply_text(
            f"Total worked time: {int(hours)}h {int(minutes)}min"
        )
    else:
        await update.message.reply_text(LANGUAGES[lang]["no_sessions"])

# Commande /reset
async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    lang = get_language(user_id)

    if user_id in user_data:
        del user_data[user_id]
        await update.message.reply_text(LANGUAGES[lang]["data_reset"])
    else:
        await update.message.reply_text(LANGUAGES[lang]["no_sessions"])

async def export(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    lang = get_language(user_id)

    if user_id not in user_data or not user_data[user_id]["sessions"]:
        await update.message.reply_text(LANGUAGES[lang]["no_sessions"])
        return

    sessions = user_data[user_id]["sessions"]

    try:
        html_content = """<html><head><style>
        table {font-family: Arial, sans-serif; border-collapse: collapse; width: 100%;}
        th, td {border: 1px solid #dddddd; text-align: left; padding: 8px;}
        th {background-color: #f2f2f2;}
        </style></head><body>
        <h2>Work Sessions</h2>
        <table>
        <tr><th>Start</th><th>End</th><th>Worked Time</th></tr>"""

        for arrive_time, depart_time, worked_time in sessions:
            hours, remainder = divmod(worked_time.total_seconds(), 3600)
            minutes = remainder // 60
            html_content += f"<tr><td>{arrive_time}</td><td>{depart_time}</td><td>{int(hours)}h {int(minutes)}min</td></tr>"

        html_content += "</table></body></html>"

        pdf_path = f"work_sessions_{user_id}.pdf"
        pdfkit.from_string(html_content, pdf_path)

        with open(pdf_path, "rb") as pdf_file:
            await update.message.reply_document(document=pdf_file)

    except Exception as e:
        await update.message.reply_text(LANGUAGES[lang]["export_failure"])

# Initialisation du bot
application = Application.builder().token(TOKEN).build()

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("add", add))
application.add_handler(CommandHandler("recap", recap))
application.add_handler(CommandHandler("reset", reset))
application.add_handler(CommandHandler("export", export))

if __name__ == "__main__":
    application.run_polling()

bdc21e8 (Fix missing import for Update)
