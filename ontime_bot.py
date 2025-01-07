from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from datetime import datetime, timedelta

# Créez l'application avec votre clé Telegram
app = Application.builder().token("7685304448:AAEuMefo6gvKOydyTtRv6pVXLMxvTuJfWr4").build()

# Messages sarcastiques
LANGUAGES = {
    "fr": {
        "start_message": (
            "✨ Bonjour {name} !\n\n"
            "Je suis ton assistant de travail, et apparemment, je dois faire le travail que tu pourrais faire toi-même. 😏\n\n"
            "Voici ce que je peux faire :\n"
            "✅ `/add` - Ajoute des horaires (ex. : `/add 10h 18h 30`).\n"
            "✅ `/recap` - Affiche le résumé de tes sessions de travail.\n"
            "✅ `/delete` - Supprime tout et fait semblant qu'on ne s'est jamais rencontrés.\n"
            "✅ `/info` - T'explique comment utiliser `/add`, au cas où tu oublies. 🙄\n\n"
            "Allez, surprends-moi ! 🚀"
        ),
        "info_message": (
            "💡 **Comment utiliser la commande /add ?**\n\n"
            "Tu entres simplement : `/add [début] [fin] [pause]`\n"
            "**Exemple :** `/add 10h30 18h 25`\n"
            "- `10h30` : Heure de début.\n"
            "- `18h` : Heure de fin (les minutes par défaut sont `00`).\n"
            "- `25` : Pause en minutes.\n\n"
            "Facile, non ? Et si tu rates, je te le ferai savoir. 🤓"
        ),
        "add_success": (
            "✨ Très bien, {name}. J'ai enregistré : {start} - {end} avec {pause} min de pause.\n"
            "Total travaillé : **{hours}**. Impressionnant, non ? 😎"
        ),
        "invalid_format": (
            "❌ Format invalide. Essaye `/add [début] [fin] [pause]`, comme `/add 10h 18h30 15`. 🤦"
        ),
        "invalid_time": (
            "⏰ Les horaires que tu as donnés ne sont pas valides. Essaye encore, et ne me fais pas perdre mon temps. 😒"
        ),
        "no_sessions": "📉 Aucune session enregistrée. Tu te reposes sur tes lauriers, apparemment. 👏",
        "recap_header": "📋 **Résumé de tes sessions** :\n",
        "data_deleted": "🚮 Toutes tes données ont été supprimées. Je suis libre maintenant. 🙃",
    }
}

# Gestion des données utilisateur
user_data = {}

def get_language(user_id):
    return user_data.get(user_id, {}).get("language", "fr")

def parse_time_format(time_str):
    """Simplifie le format des horaires en HH:MM."""
    if "h" in time_str:
        time_str = time_str.replace("h", ":")
    if len(time_str.split(":")) == 1:  # Si pas de minutes, ajoute ":00"
        time_str += ":00"
    try:
        parts = time_str.split(":")
        hours, minutes = int(parts[0]), int(parts[1])
        if 0 <= hours < 24 and 0 <= minutes < 60:
            return f"{hours:02}:{minutes:02}"
    except (ValueError, IndexError):
        return None
    return None

def calculate_hours_minutes(start, end, pause):
    """Calcule le total travaillé en heures et minutes, en déduisant la pause."""
    start_time = datetime.strptime(start, "%H:%M")
    end_time = datetime.strptime(end, "%H:%M")
    duration = (end_time - start_time).seconds // 60  # Total en minutes
    total_minutes = max(0, duration - pause)
    hours, minutes = divmod(total_minutes, 60)
    return f"{hours}h{minutes:02}"  # Format HHhMM
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    first_name = update.message.from_user.first_name
    user_data[user_id] = {"sessions": [], "language": "fr", "total_hours": "0h00"}
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
        user_data[user_id] = {"sessions": [], "language": "fr", "total_hours": "0h00"}

    user_data[user_id]["sessions"].append(f"{start}-{end} (Pause : {pause} min)")
    user_data[user_id]["total_hours"] = hours_worked

    await update.message.reply_text(
        LANGUAGES[lang]["add_success"].format(name=first_name, start=start, end=end, pause=pause, hours=hours_worked)
    )

async def recap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    lang = get_language(user_id)

    if user_id not in user_data or not user_data[user_id]["sessions"]:
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
