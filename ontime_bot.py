from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from datetime import datetime, timedelta
import pdfkit

# Dictionnaires pour les langues supportées
LANGUAGES = {
    "fr": {
        "start": "Bienvenue dans le Bot OnTime! Utilisez /add pour ajouter une session de travail, /recap pour voir les sessions et /export pour exporter en PDF.",
        "added": "Session ajoutée!",
        "recap": "Voici vos sessions de travail :",
        "no_sessions": "Aucune session disponible.",
        "export_success": "Exportation réussie!",
        "export_failure": "Échec de l'exportation.",
    },
    "en": {
        "start": "Welcome to the OnTime Bot! Use /add to log a work session, /recap to view sessions, and /export to export to PDF.",
        "added": "Session added!",
        "recap": "Here are your work sessions:",
        "no_sessions": "No sessions available.",
        "export_success": "Export successful!",
        "export_failure": "Export failed.",
    }
}

# Données utilisateurs
user_data = {}

# Fonction pour récupérer la langue de l'utilisateur
def get_language(user_id):
    return user_data.get(user_id, {}).get("language", "en")

# Commande /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_data[user_id] = user_data.get(user_id, {"sessions": [], "language": "en"})
    lang = get_language(user_id)
    await update.message.reply_text(LANGUAGES[lang]["start"])

# Commande /add
async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    lang = get_language(user_id)

    if user_id not in user_data:
        user_data[user_id] = {"sessions": [], "language": "en"}

    now = datetime.now()
    session = (now.strftime("%Y-%m-%d %H:%M:%S"), now.strftime("%Y-%m-%d %H:%M:%S"), timedelta(hours=1))
    user_data[user_id]["sessions"].append(session)

    await update.message.reply_text(LANGUAGES[lang]["added"])

# Commande /recap
async def recap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    lang = get_language(user_id)

    if user_id not in user_data or not user_data[user_id]["sessions"]:
        await update.message.reply_text(LANGUAGES[lang]["no_sessions"])
        return

    recap_message = LANGUAGES[lang]["recap"]
    for arrive_time, depart_time, worked_time in user_data[user_id]["sessions"]:
        hours, remainder = divmod(worked_time.total_seconds(), 3600)
        minutes = remainder // 60
        recap_message += f"\nArrivée : {arrive_time}, Départ : {depart_time}, Temps travaillé : {int(hours)}h {int(minutes)}min"

    await update.message.reply_text(recap_message)
import datetime
from typing import Dict
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Gestion des langues
LANGUAGES = {
    "en": {
        "welcome": "Welcome! Use /add to log your work hours.",
        "arrival_logged": "Arrival logged at {time}!",
        "departure_logged": "Departure logged at {time}!",
        "no_sessions": "No sessions logged yet.",
        "recap_header": "Work recap:",
        "reset_success": "All sessions have been reset!",
        "export_failure": "Failed to export sessions.",
    },
    "fr": {
        "welcome": "Bienvenue! Utilisez /add pour enregistrer vos heures de travail.",
        "arrival_logged": "Arrivée enregistrée à {time}!",
        "departure_logged": "Départ enregistré à {time}!",
        "no_sessions": "Aucune session enregistrée pour l'instant.",
        "recap_header": "Récapitulatif des heures de travail :",
        "reset_success": "Toutes les sessions ont été réinitialisées !",
        "export_failure": "Échec de l'exportation des sessions.",
    },
    "uk": {
        "welcome": "Ласкаво просимо! Використовуйте /add для запису своїх годин роботи.",
        "arrival_logged": "Прибуття зафіксовано о {time}!",
        "departure_logged": "Відбуття зафіксовано о {time}!",
        "no_sessions": "Жодної сесії ще не зареєстровано.",
        "recap_header": "Огляд роботи:",
        "reset_success": "Усі сесії були скинуті!",
        "export_failure": "Не вдалося експортувати сесії.",
    }
}

user_data: Dict[int, Dict] = {}

# Fonction pour récupérer la langue d'un utilisateur
def get_language(user_id: int) -> str:
    return user_data.get(user_id, {}).get("lang", "en")

# Commande /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_data[user_id] = {"lang": "en", "sessions": []}
    lang = get_language(user_id)
    await update.message.reply_text(LANGUAGES[lang]["welcome"])

# Commande /add
async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    lang = get_language(user_id)

    if "sessions" not in user_data[user_id]:
        user_data[user_id]["sessions"] = []

    now = datetime.datetime.now()
    if not user_data[user_id]["sessions"] or user_data[user_id]["sessions"][-1][1] is not None:
        user_data[user_id]["sessions"].append([now, None, None])
        await update.message.reply_text(LANGUAGES[lang]["arrival_logged"].format(time=now.strftime("%H:%M")))
    else:
        start_time = user_data[user_id]["sessions"][-1][0]
        worked_time = now - start_time
        user_data[user_id]["sessions"][-1][1] = now
        user_data[user_id]["sessions"][-1][2] = worked_time
        await update.message.reply_text(LANGUAGES[lang]["departure_logged"].format(time=now.strftime("%H:%M")))
# Partie 3 : Exportation en PDF et ajout des handlers pour les commandes

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

# Ajout des handlers pour les commandes
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("add", add))
application.add_handler(CommandHandler("recap", recap))
application.add_handler(CommandHandler("reset", reset))
application.add_handler(CommandHandler("export", export))

if __name__ == "__main__":
    application.run_polling()

