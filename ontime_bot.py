from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from datetime import datetime, timedelta

# Créez l'application avec votre clé Telegram
app = Application.builder().token("7685304448:AAEuMefo6gvKOydyTtRv6pVXLMxvTuJfWr4").build()

# Fonction utilitaire pour échapper les caractères spéciaux pour MarkdownV2
def escape_markdown_v2(text):
    special_characters = r"_*[]()~`>#+-=|{}.!"
    for char in special_characters:
        text = text.replace(char, f"\\{char}")
    return text

# Dictionnaire des messages sarcastiques en plusieurs langues
LANGUAGES = {
    "fr": {
        "start_message": (
            "✨ Bonjour {name} !\n\n"
            "Je suis ton assistant bot 🤖, prêt à suivre tes horaires de travail. 😏\n\n"
            "Voici ce que je peux faire pour toi :\n"
            "/start - Me démarrer.\n"
            "/add - Ajouter des horaires avec pause (ex. : /add 10h28 20h35 25).\n"
            "/recap - Obtenir un récapitulatif de ton travail.\n"
            "/delete - Supprimer toutes tes données.\n"
            "/info - Voir les instructions pour utiliser /add.\n\n"
            "Alors, prêt à commencer ? 🚀"
        ),
        "info_message": (
            "💡 **Comment utiliser la commande /add ?**\n\n"
            "La commande /add fonctionne ainsi :\n"
            "`/add [début] [fin] [pause]`\n\n"
            "**Exemple :** `/add 10h28 20h35 25`\n"
            "- `10h28` : Heure de début.\n"
            "- `20h35` : Heure de fin.\n"
            "- `25` : Minutes de pause.\n\n"
            "Je calculerai automatiquement le temps travaillé en déduisant la pause. 🕒"
        ),
        "add_success": (
            "✨ Très bien {name}, j'ai ajouté ça : {start} - {end} avec {pause} min de pause.\n"
            "Total d'heures travaillées : {hours}.\n\n"
            "Continue comme ça. 🤓"
        ),
        "invalid_format": (
            "❌ Format invalide. Utilise `/add [début] [fin] [pause]` (ex. : `/add 10h28 20h35 25`)."
        ),
        "invalid_time": (
            "⏰ Les horaires que tu as entrés sont invalides. Essaye encore. 😒"
        ),
        "no_sessions": "Tu n'as enregistré aucune session. Félicitations pour ton inactivité. 👏",
        "recap_header": "📋 Voici un récapitulatif de tes sessions de travail :\n",
        "data_deleted": "🚮 Toutes tes données ont été supprimées.",
    }
}

# Gestion des données utilisateur
user_data = {}

def get_language(user_id):
    return user_data.get(user_id, {}).get("language", "fr")

def parse_time_format(time_str):
    """Convertit différents formats d'horaires en HH:MM."""
    if "h" in time_str:
        time_str = time_str.replace("h", ":")
    parts = time_str.split(":")
    if len(parts) != 2 or not parts[0].isdigit() or not parts[1].isdigit():
        return None
    hours, minutes = map(int, parts)
    if not (0 <= hours < 24 and 0 <= minutes < 60):
        return None
    return f"{hours:02}:{minutes:02}"

def calculate_hours_minutes(start, end, pause):
    """Calcule les heures et minutes travaillées en déduisant la pause."""
    start_time = datetime.strptime(start, "%H:%M")
    end_time = datetime.strptime(end, "%H:%M")
    duration = (end_time - start_time).seconds // 60  # Convertir en minutes
    total_minutes = max(0, duration - pause)
    hours, minutes = divmod(total_minutes, 60)
    return f"{hours}h{minutes:02}"  # Format HHhMM
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    first_name = update.message.from_user.first_name
    user_data[user_id] = {"sessions": [], "language": "fr", "total_hours": 0}
    lang = get_language(user_id)
    await update.message.reply_text(LANGUAGES[lang]["start_message"].format(name=first_name))

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    lang = get_language(user_id)
    await update.message.reply_text(LANGUAGES[lang]["info_message"])

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    first_name = update.message.from_user.first_name
    lang = get_language(user_id)
    message = update.message.text.split(" ")

    if len(message) != 4:  # Vérifie qu'il y a exactement trois arguments
        await update.message.reply_text(LANGUAGES[lang]["invalid_format"])
        return

    start = parse_time_format(message[1])
    end = parse_time_format(message[2])
    try:
        pause = int(message[3])  # Pause en minutes
    except ValueError:
        await update.message.reply_text(LANGUAGES[lang]["invalid_format"])
        return

    if not start or not end or pause < 0:
        await update.message.reply_text(LANGUAGES[lang]["invalid_time"])
        return

    hours_worked = calculate_hours_minutes(start, end, pause)

    if user_id not in user_data:
        user_data[user_id] = {"sessions": [], "language": "fr", "total_hours": 0}

    user_data[user_id]["sessions"].append(f"{start}-{end} (Pause : {pause} min)")
    user_data[user_id]["total_hours"] = hours_worked

    await update.message.reply_text(
        LANGUAGES[lang]["add_success"].format(name=first_name, start=start, end=end, pause=pause, hours=hours_worked)
    )

async def recap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    lang = get_language(user_id)

    if user_id not in user_data or "sessions" not in user_data[user_id] or not user_data[user_id]["sessions"]:
        await update.message.reply_text(LANGUAGES[lang]["no_sessions"])
        return

    recap_message = LANGUAGES[lang]["recap_header"]
    for idx, session in enumerate(user_data[user_id]["sessions"], start=1):
        recap_message += f"\n{idx}. {session}"

    await update.message.reply_text(recap_message)

async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    lang = get_language(user_id)

    if user_id in user_data:
        user_data.pop(user_id)

    await update.message.reply_text(LANGUAGES[lang]["data_deleted"])

# Ajout des handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("info", info))
app.add_handler(CommandHandler("add", add))
app.add_handler(CommandHandler("recap", recap))
app.add_handler(CommandHandler("delete", delete))

# Lancement du bot
if __name__ == "__main__":
    app.run_polling()
