from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from transformers import pipeline

# Charger le modèle d'IA Hugging Face
chatbot = pipeline("text-generation", model="distilgpt2")

# Token du bot Telegram
BOT_TOKEN = "7685304448:AAEuMefo6gvKOydyTtRv6pVXLMxvTuJfWr4"

# Créer l'application Telegram
app = Application.builder().token(BOT_TOKEN).build()

# Dictionnaire des messages en plusieurs langues
LANGUAGES = {
    "fr": {
        "start_message": (
            "Salut 👋 ! Je suis ton assistant (un peu sarcastique). Voici ce que je peux faire :\n\n"
            "/start - Me dire bonjour et découvrir mes commandes.\n"
            "/add <heure1> <heure2> <pause> - Ajouter une session de travail.\n"
            "/recap - Voir un récapitulatif des heures travaillées.\n"
            "/delete - Effacer toutes les données enregistrées.\n"
            "/chat - Parle-moi de tout et de rien grâce à l'IA !\n"
            "/info - Apprendre à utiliser les commandes. 📜"
        ),
        "info_message": "Utilise /add comme suit : '/add 08h30 17h00 60' pour indiquer une journée de travail de 8h30 à 17h00 avec 60 minutes de pause.",
        "add_success": "Heures ajoutées avec succès ! ✅",
        "recap_empty": "Aucune donnée enregistrée pour le moment. 😅",
        "data_deleted": "Toutes tes données ont été supprimées. 🗑️",
    },
    "en": {
        "start_message": (
            "Hi 👋! I'm your assistant (a bit sarcastic). Here's what I can do:\n\n"
            "/start - Say hello and discover my commands.\n"
            "/add <time1> <time2> <break> - Add a work session.\n"
            "/recap - See a summary of your worked hours.\n"
            "/delete - Delete all recorded data.\n"
            "/chat - Chat with me about anything using AI!\n"
            "/info - Learn how to use the commands. 📜"
        ),
        "info_message": "Use /add like this: '/add 08:30 17:00 60' to record a work session from 08:30 to 17:00 with a 60-minute break.",
        "add_success": "Hours successfully added! ✅",
        "recap_empty": "No data recorded yet. 😅",
        "data_deleted": "All your data has been deleted. 🗑️",
    },
}

# Stockage des données utilisateur
user_data = {}
from datetime import datetime, timedelta

# Obtenir la langue d'un utilisateur
def get_language(user_id):
    return user_data.get(user_id, {}).get("language", "fr")

# Commande /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    lang = get_language(user_id)
    await update.message.reply_text(LANGUAGES[lang]["start_message"])

# Commande /info
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    lang = get_language(user_id)
    await update.message.reply_text(LANGUAGES[lang]["info_message"])

# Commande /add
async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    lang = get_language(user_id)
    text = update.message.text.split()

    if len(text) != 4:
        await update.message.reply_text(LANGUAGES[lang]["info_message"])
        return

    try:
        start_time = datetime.strptime(text[1].replace("h", ":"), "%H:%M")
        end_time = datetime.strptime(text[2].replace("h", ":"), "%H:%M")
        pause_minutes = int(text[3])
    except ValueError:
        await update.message.reply_text(LANGUAGES[lang]["info_message"])
        return

    work_duration = end_time - start_time - timedelta(minutes=pause_minutes)
    if user_id not in user_data:
        user_data[user_id] = {"sessions": [], "language": lang}
    user_data[user_id]["sessions"].append(work_duration)

    total_hours, remainder = divmod(work_duration.seconds, 3600)
    total_minutes = remainder // 60

    await update.message.reply_text(
        f"Travail enregistré : {total_hours}h{total_minutes} après une pause de {pause_minutes} minutes. 🕒"
    )

# Commande /recap
async def recap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    lang = get_language(user_id)

    if user_id not in user_data or not user_data[user_id]["sessions"]:
        await update.message.reply_text(LANGUAGES[lang]["recap_empty"])
        return

    recap_message = "📋 *Récapitulatif des heures travaillées :*\n"
    for idx, session in enumerate(user_data[user_id]["sessions"], start=1):
        total_hours, remainder = divmod(session.seconds, 3600)
        total_minutes = remainder // 60
        recap_message += f"{idx}. {total_hours}h{total_minutes}\n"

    await update.message.reply_text(recap_message)

# Commande /delete
async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    lang = get_language(user_id)

    if user_id in user_data:
        user_data[user_id]["sessions"] = []
    await update.message.reply_text(LANGUAGES[lang]["data_deleted"])
# Commande pour discuter avec l'IA
async def chat_with_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    response = chatbot(user_message, max_length=50, num_return_sequences=1)[0]["generated_text"]

    await update.message.reply_text(response)

# Ajouter les gestionnaires de commandes
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("info", info))
app.add_handler(CommandHandler("add", add))
app.add_handler(CommandHandler("recap", recap))
app.add_handler(CommandHandler("delete", delete))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_with_ai))

# Exécuter le bot
if __name__ == "__main__":
    app.run_polling()
