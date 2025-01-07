from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, Filters, ContextTypes
from transformers import pipeline

# Charger un modèle Hugging Face (GPT-2 utilisé ici comme exemple)
generator = pipeline("text-generation", model="gpt2")

# Créez l'application avec votre clé Telegram
app = Application.builder().token("VOTRE_TOKEN_TELEGRAM").build()

# Fonction utilitaire pour échapper les caractères spéciaux pour MarkdownV2
def escape_markdown_v2(text):
    special_characters = r"_[]()~`>#+-=|{}.!"
    for char in special_characters:
        text = text.replace(char, f"\\{char}")
    return text

# Dictionnaire des messages en plusieurs langues
LANGUAGES = {
    "fr": {
        "start_message": (
            "Bonjour ! Je suis votre assistant. Voici ce que je peux faire :\n\n"
            "Commandes disponibles :\n"
            "/add [heure début] [heure fin] [minutes pause] - Ajouter vos horaires de travail.\n"
            "/info - Voir comment fonctionne le bot.\n"
            "/clear - Supprimer toutes vos données.\n\n"
            "💡 Vous pouvez aussi me poser des questions ou discuter avec moi directement."
        ),
        "add_success": "C'est ajouté. Temps travaillé calculé avec succès.",
        "no_sessions": "Aucune session enregistrée pour le moment.",
        "session_saved": "Session sauvegardée.",
        "data_cleared": "Toutes vos données ont été supprimées.",
        "ai_response": "Voici ce que je pense :"
    },
    "en": {
        "start_message": (
            "Hello! I'm your assistant. Here's what I can do:\n\n"
            "Available commands:\n"
            "/add [start time] [end time] [break minutes] - Add your work hours.\n"
            "/info - Learn how this bot works.\n"
            "/clear - Delete all your data.\n\n"
            "💡 You can also ask me questions or chat with me directly."
        ),
        "add_success": "Added successfully. Work hours calculated.",
        "no_sessions": "No sessions recorded yet.",
        "session_saved": "Session saved.",
        "data_cleared": "All your data has been cleared.",
        "ai_response": "Here's my response:"
    },
}

# Fonction utilitaire pour obtenir la langue d'un utilisateur
def get_language(user_id):
    return user_data.get(user_id, {}).get("language", "fr")
# Dictionnaire global pour stocker les données utilisateur
user_data = {}

# Commande /start
async def start(update: Update, context: ContextTypes.DEFAULT
_TYPE):
    user_id = update.message.from_user.id
    if user_id not in user_data:
        user_data[user_id] = {"sessions": [], "language": "fr"}
    lang = get_language(user_id)
    await update.message.reply_text(LANGUAGES[lang]["start_message"])

# Commande /add pour ajouter une session de travail
async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    message = update.message.text
    lang = get_language(user_id)

    try:
        parts = message.split()[1:]
        start_time = parts[0]
        end_time = parts[1]
        break_minutes = int(parts[2]) if len(parts) > 2 else 0

        # Calculer le temps de travail
        start_hour, start_minute = map(int, start_time.replace("h", ":").split(":"))
        end_hour, end_minute = map(int, end_time.replace("h", ":").split(":"))

        total_minutes = ((end_hour * 60 + end_minute) - (start_hour * 60 + start_minute)) - break_minutes
        worked_hours = total_minutes // 60
        worked_minutes = total_minutes % 60

        if user_id not in user_data:
            user_data[user_id] = {"sessions": [], "language": "fr"}

        user_data[user_id]["sessions"].append({
            "start": start_time,
            "end": end_time,
            "break": break_minutes,
            "worked": f"{worked_hours}h{worked_minutes:02d}"
        })

        await update.message.reply_text(
            f"{LANGUAGES[lang]['add_success']}\nTemps travaillé : {worked_hours}h{worked_minutes:02d}."
        )
    except (IndexError, ValueError):
        await update.message.reply_text(
            "Format invalide. Essayez comme ça : /add 10h28 20h35 25"
        )

# Commande /clear pour supprimer toutes les données utilisateur
async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    lang = get_language(user_id)

    if user_id in user_data:
        user_data.pop(user_id)
    await update.message.reply_text(LANGUAGES[lang]["data_cleared"])

# Commande /info pour expliquer le fonctionnement
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    lang = get_language(user_id)
    await update.message.reply_text(LANGUAGES[lang]["start_message"])
_TYPE):
    user_id = update.message.from_user.id
    if user_id not in user_data:
        user_data[user_id] = {"sessions": [], "language": "fr"}
    lang = get_language(user_id)
    await update.message.reply_text(LANGUAGES[lang]["start_message"])

# Commande /add pour ajouter une session de travail
async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    message = update.message.text
    lang = get_language(user_id)

    try:
        parts = message.split()[1:]
        start_time = parts[0]
        end_time = parts[1]
        break_minutes = int(parts[2]) if len(parts) > 2 else 0

        # Calculer le temps de travail
        start_hour, start_minute = map(int, start_time.replace("h", ":").split(":"))
        end_hour, end_minute = map(int, end_time.replace("h", ":").split(":"))

        total_minutes = ((end_hour * 60 + end_minute) - (start_hour * 60 + start_minute)) - break_minutes
        worked_hours = total_minutes // 60
        worked_minutes = total_minutes % 60

        if user_id not in user_data:
            user_data[user_id] = {"sessions": [], "language": "fr"}

        user_data[user_id]["sessions"].append({
            "start": start_time,
            "end": end_time,
            "break": break_minutes,
            "worked": f"{worked_hours}h{worked_minutes:02d}"
        })

        await update.message.reply_text(
            f"{LANGUAGES[lang]['add_success']}\nTemps travaillé : {worked_hours}h{worked_minutes:02d}."
        )
    except (IndexError, ValueError):
        await update.message.reply_text(
            "Format invalide. Essayez comme ça : /add 10h28 20h35 25"
        )

# Commande /clear pour supprimer toutes les données utilisateur
async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    lang = get_language(user_id)

    if user_id in user_data:
        user_data.pop(user_id)
    await update.message.reply_text(LANGUAGES[lang]["data_cleared"])

# Commande /info pour expliquer le fonctionnement
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    lang = get_language(user_id)
    await update.message.reply_text(LANGUAGES[lang]["start_message"])
# Fonction pour traiter les messages non associés à des commandes (discussions avec l'IA)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    lang = get_language(user_id)
    message = update.message.text

    try:
        response = generator(message, max_length=50, num_return_sequences=1)
        ai_text = response[0]["generated_text"]
        await update.message.reply_text(f"{LANGUAGES[lang]['ai_response']}\n{ai_text}")
    except Exception as e:
        await update.message.reply_text("Désolé, une erreur est survenue avec l'IA.")

# Ajout des handlers au bot
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("add", add))
app.add_handler(CommandHandler("clear", clear))
app.add_handler(CommandHandler("info", info))
app.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

# Démarrage du bot
if __name__ == "__main__":
    app.run_polling()
