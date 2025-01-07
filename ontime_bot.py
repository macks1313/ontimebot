from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import os

# Configuration du bot avec le token
TOKEN = "7685304448:AAEuMefo6gvKOydyTtRv6pVXLMxvTuJfWr4"
app = Application.builder().token(TOKEN).build()

# Dictionnaire des langues prises en charge
LANGUAGES = {
    "en": {
        "start": "Welcome! I am your assistant bot.",
        "help": "You can use commands like /add, /recap, /save_session.",
        "add_success": "Added to the current session.",
        "recap_header": "Here is the recap of your sessions:",
        "session_saved": "Session saved successfully.",
        "no_sessions": "You have no sessions recorded.",
        "no_active_session": "No active session to save.",
        "lang_set": "Language set to English."
    },
    "fr": {
        "start": "Bienvenue ! Je suis votre bot assistant.",
        "help": "Vous pouvez utiliser des commandes comme /add, /recap, /save_session.",
        "add_success": "Ajouté à la session en cours.",
        "recap_header": "Voici le récapitulatif de vos sessions :",
        "session_saved": "Session enregistrée avec succès.",
        "no_sessions": "Vous n'avez aucune session enregistrée.",
        "no_active_session": "Aucune session active à enregistrer.",
        "lang_set": "Langue définie sur le français."
    }
}

# Commande /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_data[user_id] = {"sessions": [], "language": "en"}
    lang = get_language(user_id)
    await update.message.reply_text(LANGUAGES[lang]["start"])

# Commande /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_language(update.message.from_user.id)
    await update.message.reply_text(LANGUAGES[lang]["help"])

# Commande pour changer de langue
async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    lang_code = context.args[0] if context.args else "en"

    if lang_code in LANGUAGES:
        user_data[user_id]["language"] = lang_code
        await update.message.reply_text(LANGUAGES[lang_code]["lang_set"])
    else:
        await update.message.reply_text("Language not supported.")
# Dictionnaire global pour stocker les données utilisateur
user_data = {}

# Fonction utilitaire pour obtenir la langue d'un utilisateur
def get_language(user_id):
    return user_data.get(user_id, {}).get("language", "en")

# Commande /add
async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    message = update.message.text

    if user_id not in user_data:
        user_data[user_id] = {"sessions": [], "language": "en"}

    if "current_session" not in user_data[user_id]:
        user_data[user_id]["current_session"] = []

    user_data[user_id]["current_session"].append(message)
    lang = get_language(user_id)
    await update.message.reply_text(LANGUAGES[lang]["add_success"])

# Commande /recap
async def recap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    lang = get_language(user_id)

    if user_id not in user_data or not user_data[user_id]["sessions"]:
        await update.message.reply_text(LANGUAGES[lang]["no_sessions"])
        return

    recap_message = LANGUAGES[lang]["recap_header"]
    for idx, session in enumerate(user_data[user_id]["sessions"], start=1):
        recap_message += f"\n{idx}. {', '.join(session)}"

    await update.message.reply_text(recap_message)

# Commande /save_session
async def save_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    lang = get_language(user_id)

    if user_id not in user_data or "current_session" not in user_data[user_id]:
        await update.message.reply_text(LANGUAGES[lang]["no_active_session"])
        return

    user_data[user_id]["sessions"].append(user_data[user_id]["current_session"])
    user_data[user_id].pop("current_session")
    await update.message.reply_text(LANGUAGES[lang]["session_saved"])

# Ajout des handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("set_language", set_language))
app.add_handler(CommandHandler("add", add))
app.add_handler(CommandHandler("recap", recap))
app.add_handler(CommandHandler("save_session", save_session))

# Lancement de l'application
if __name__ == "__main__":
    app.run_polling()
