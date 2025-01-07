from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from datetime import datetime

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
            "Je suis ton assistant bot 🤖, prêt à suivre tes horaires de travail, car apparemment tu ne peux pas le faire toi-même. 😏\n\n"
            "Voici ce que je peux faire pour toi :\n"
            "/start - Me démarrer.\n"
            "/add - Ajouter des horaires (formats acceptés : HHhMM, HH:MM, HhMM, etc.).\n"
            "/recap - Obtenir un récapitulatif de ton labeur épique.\n"
            "/delete - Supprimer toutes tes données.\n\n"
            "Dis-moi, ô maître, que puis-je faire pour toi aujourd'hui ? 😎"
        ),
        "add_success": (
            "✨ Très bien {name}, j'ai ajouté ça à ta session. Total d'heures travaillées : {hours:.2f} heures.\n\n"
            "Continue comme ça. 🤓"
        ),
        "invalid_format": "Euh… pardon ? Ce format est incompréhensible. Essaie : HHhMM, HH:MM ou HhMM. 🧐",
        "invalid_time": "⏰ Les horaires que tu as entrés sont invalides. Essaye encore. 😒",
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

def calculate_hours(start, end):
    """Calcule les heures entre deux horaires."""
    start_time = datetime.strptime(start, "%H:%M")
    end_time = datetime.strptime(end, "%H:%M")
    duration = (end_time - start_time).seconds / 3600  # Convertir en heures
    return duration

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    first_name = update.message.from_user.first_name
    user_data[user_id] = {"sessions": [], "language": "fr", "total_hours": 0}
    lang = get_language(user_id)
    await update.message.reply_text(LANGUAGES[lang]["start_message"].format(name=first_name))
async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    first_name = update.message.from_user.first_name
    lang = get_language(user_id)
    message = update.message.text

    if user_id not in user_data:
        user_data[user_id] = {"sessions": [], "language": "fr", "total_hours": 0}

    try:
        time_range = message.split(" ")[1]
        start, end = time_range.split("-")
        start = parse_time_format(start)
        end = parse_time_format(end)

        if not start or not end:
            await update.message.reply_text(LANGUAGES[lang]["invalid_time"])
            return

        hours = calculate_hours(start, end)

        if "current_session" not in user_data[user_id]:
            user_data[user_id]["current_session"] = []

        user_data[user_id]["current_session"].append(f"{start}-{end}")
        user_data[user_id]["sessions"].append(user_data[user_id]["current_session"])
        user_data[user_id]["current_session"] = []
        user_data[user_id]["total_hours"] += hours

        await update.message.reply_text(
            LANGUAGES[lang]["add_success"].format(name=first_name, hours=user_data[user_id]["total_hours"])
        )
    except (ValueError, IndexError):
        await update.message.reply_text(LANGUAGES[lang]["invalid_format"])

async def recap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    lang = get_language(user_id)

    if user_id not in user_data or "sessions" not in user_data[user_id] or not user_data[user_id]["sessions"]:
        await update.message.reply_text(LANGUAGES[lang]["no_sessions"])
        return

    recap_message = LANGUAGES[lang]["recap_header"]
    for idx, session in enumerate(user_data[user_id]["sessions"], start=1):
        recap_message += f"\n{idx}. {', '.join(session)}"

    await update.message.reply_text(recap_message)

async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    lang = get_language(user_id)

    if user_id in user_data:
        user_data.pop(user_id)

    await update.message.reply_text(LANGUAGES[lang]["data_deleted"])

# Ajout des handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("add", add))
app.add_handler(CommandHandler("recap", recap))
app.add_handler(CommandHandler("delete", delete))

# Lancement du bot
if __name__ == "__main__":
    app.run_polling()
