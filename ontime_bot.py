from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from transformers import pipeline

# Configuration du modèle Hugging Face
ai_pipeline = pipeline("text-generation", model="gpt2")  # Tu peux remplacer par un autre modèle Hugging Face.

# Crée l'application avec ton token Telegram
app = Application.builder().token("7685304448:AAEuMefo6gvKOydyTtRv6pVXLMxvTuJfWr4").build()

# Fonction pour échapper les caractères spéciaux pour MarkdownV2
def escape_markdown_v2(text):
    special_characters = r"_*[]()~`>#+-=|{}.!"
    for char in special_characters:
        text = text.replace(char, f"\\{char}")
    return text

# Dictionnaire des messages multilingues
LANGUAGES = {
    "fr": {
        "start_message": "Bonjour ! Je suis ton assistant intelligent 🤖. Utilise /add pour ajouter des heures ou commence une discussion pour voir ce que je peux faire !",
        "help_message": (
            "Voici les commandes disponibles :\n"
            "👉 /start - Démarrer le bot\n"
            "👉 /add [horaire début] [horaire fin] [pause en minutes] - Calculer les heures travaillées\n"
            "👉 /delete - Supprimer toutes les données enregistrées\n"
            "👉 /info - En savoir plus sur le fonctionnement du bot\n"
        ),
        "info_message": (
            "La commande /add fonctionne ainsi :\n"
            "1️⃣ Fournis les horaires de début et de fin au format 08h30, 17h45 ou 10:15.\n"
            "2️⃣ Indique la durée de pause en minutes (optionnelle).\n"
            "Je calcule pour toi les heures travaillées avec précision !\n\n"
            "Parle-moi librement pour utiliser mon IA. 😊"
        ),
        "data_deleted": "Toutes les données ont été supprimées 🗑️.",
    },
    "en": {
        "start_message": "Hello! I'm your smart assistant 🤖. Use /add to add hours or start chatting to see what I can do!",
        "help_message": (
            "Here are the available commands:\n"
            "👉 /start - Start the bot\n"
            "👉 /add [start time] [end time] [pause in minutes] - Calculate working hours\n"
            "👉 /delete - Delete all saved data\n"
            "👉 /info - Learn more about how the bot works\n"
        ),
        "info_message": (
            "The /add command works as follows:\n"
            "1️⃣ Provide start and end times in the format 08h30, 17h45, or 10:15.\n"
            "2️⃣ Specify the break duration in minutes (optional).\n"
            "I'll calculate the worked hours for you with precision!\n\n"
            "Feel free to talk to me to use my AI. 😊"
        ),
        "data_deleted": "All data has been deleted 🗑️.",
    },
}

# Dictionnaire global pour stocker les données utilisateur
user_data = {}

# Fonction utilitaire pour obtenir la langue de l'utilisateur
def get_language(user_id):
    return user_data.get(user_id, {}).get("language", "fr")  # Par défaut, français.

# Commande /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_data[user_id] = {"sessions": [], "language": "fr"}  # Par défaut, français.
    lang = get_language(user_id)
    await update.message.reply_text(LANGUAGES[lang]["start_message"])

# Commande /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    lang = get_language(user_id)
    await update.message.reply_text(LANGUAGES[lang]["help_message"])
import re
from datetime import datetime, timedelta

# Commande /add
async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    lang = get_language(user_id)

    try:
        # Analyse des arguments
        args = context.args
        if len(args) < 2:
            raise ValueError("Pas assez d'arguments.")

        start_time = args[0]
        end_time = args[1]
        pause_minutes = int(args[2]) if len(args) > 2 else 0

        # Fonction pour analyser les heures
        def parse_time(time_str):
            formats = ["%Hh%M", "%H:%M", "%Hh%M", "%H:%M", "%H%M"]
            for fmt in formats:
                try:
                    return datetime.strptime(time_str, fmt)
                except ValueError:
                    continue
            raise ValueError(f"Format d'heure invalide : {time_str}")

        start = parse_time(start_time)
        end = parse_time(end_time)

        # Calcul des heures travaillées
        work_duration = end - start
        if work_duration.total_seconds() < 0:
            work_duration += timedelta(days=1)  # Pour gérer les horaires après minuit

        work_duration -= timedelta(minutes=pause_minutes)

        # Formatage des heures
        hours, remainder = divmod(work_duration.total_seconds(), 3600)
        minutes = remainder // 60
        result = f"{int(hours)}h{int(minutes):02d}"

        # Sauvegarder automatiquement
        if user_id not in user_data:
            user_data[user_id] = {"sessions": [], "language": "fr"}
        user_data[user_id]["sessions"].append(
            {"start": start_time, "end": end_time, "pause": pause_minutes, "worked": result}
        )

        await update.message.reply_text(f"✅ Vous avez travaillé {result} (pause déduite).")
    except ValueError as e:
        await update.message.reply_text(f"⚠️ Erreur : {e}")

# Commande /delete
async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    lang = get_language(user_id)

    if user_id in user_data:
        user_data[user_id]["sessions"] = []
        await update.message.reply_text(LANGUAGES[lang]["data_deleted"])
    else:
        await update.message.reply_text("⚠️ Aucune donnée à supprimer.")

# Commande /info
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    lang = get_language(user_id)
    await update.message.reply_text(LANGUAGES[lang]["info_message"])

# Gérer les messages texte
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    response = ai_pipeline(user_message, max_length=50, num_return_sequences=1)[0]["generated_text"]
    await update.message.reply_text(response)

# Ajout des gestionnaires de commandes
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("add", add))
app.add_handler(CommandHandler("delete", delete))
app.add_handler(CommandHandler("info", info))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
