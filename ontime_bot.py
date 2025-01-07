from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Créez l'application avec votre clé Telegram
app = Application.builder().token("7685304448:AAEuMefo6gvKOydyTtRv6pVXLMxvTuJfWr4").build()

# Fonction utilitaire pour échapper les caractères spéciaux pour MarkdownV2
def escape_markdown_v2(text):
    special_characters = r"_*[]()~`>#+-=|{}.!"
    for char in special_characters:
        text = text.replace(char, f"\\{char}")
    return text

# Dictionnaire des messages en plusieurs langues
LANGUAGES = {
    "fr": {
        "start_message": (
            "Bonjour {name} ! Je suis là pour vous aider à suivre vos horaires de travail.\n\n"
            "Voici les commandes que je comprends :\n"
            "/start - Me démarrer.\n"
            "/help - Voir la liste des commandes.\n"
            "/language - Changer ma langue (Anglais, Français, Ukrainien).\n"
            "/add - Ajouter des horaires de travail (formats acceptés : HH:MM, HHhMM, HhMM).\n"
            "/recap - Obtenir un résumé de vos sessions enregistrées.\n"
            "/save_session - Enregistrer la session actuelle.\n\n"
            "Que puis-je faire pour vous aujourd'hui ? 😊"
        ),
        "add_success": "Très bien {name}, j'ai ajouté ça à votre session. Heures totales travaillées : {hours:.2f} heures.",
        "invalid_format": "Je n'ai pas compris le format. Essayez l'un des formats suivants : HH:MM, HHhMM ou HhMM.",
        "no_sessions": "Vous n'avez enregistré aucune session pour l'instant.",
        "recap_header": "Voici un récapitulatif de vos sessions :",
        "session_saved": "Session actuelle sauvegardée avec succès.",
        "no_active_session": "Aucune session active à sauvegarder.",
    },
    "en": {
        "start_message": (
            "Hello {name}! I'm here to help you track your working hours.\n\n"
            "Here are the commands I understand:\n"
            "/start - Start me.\n"
            "/help - See the list of commands.\n"
            "/language - Change my language (English, French, Ukrainian).\n"
            "/add - Add working hours (formats accepted: HH:MM, HHhMM, HhMM).\n"
            "/recap - Get a summary of your saved sessions.\n"
            "/save_session - Save the current session.\n\n"
            "How can I assist you today? 😊"
        ),
        "add_success": "Alright {name}, I've added that to your session. Total hours worked: {hours:.2f} hours.",
        "invalid_format": "I couldn't understand the format. Try one of the following formats: HH:MM, HHhMM, or HhMM.",
        "no_sessions": "You have no recorded sessions yet.",
        "recap_header": "Here is a summary of your sessions:",
        "session_saved": "Current session successfully saved.",
        "no_active_session": "No active session to save.",
    },
    "uk": {
        "start_message": (
            "Привіт {name}! Я тут, щоб допомогти вам відстежувати години роботи.\n\n"
            "Ось команди, які я розумію:\n"
            "/start - Запустити мене.\n"
            "/help - Подивитися список команд.\n"
            "/language - Змінити мою мову (Англійська, Французька, Українська).\n"
            "/add - Додати години роботи (формати: HH:MM, HHhMM, HhMM).\n"
            "/recap - Отримати зведення ваших сесій.\n"
            "/save_session - Зберегти поточну сесію.\n\n"
            "Чим я можу вам допомогти сьогодні? 😊"
        ),
        "add_success": "Гаразд {name}, я додав це до вашої сесії. Загальна кількість годин: {hours:.2f} год.",
        "invalid_format": "Я не зрозумів формат. Спробуйте один із наступних форматів: HH:MM, HHhMM або HhMM.",
        "no_sessions": "У вас ще немає збережених сесій.",
        "recap_header": "Ось зведення ваших сесій:",
        "session_saved": "Поточну сесію успішно збережено.",
        "no_active_session": "Немає активної сесії для збереження.",
    },
}
from datetime import datetime

# Fonction pour obtenir la langue d'un utilisateur
user_data = {}

def get_language(user_id):
    return user_data.get(user_id, {}).get("language", "fr")

def calculate_hours(start, end):
    """Calcule les heures entre deux horaires."""
    start_time = datetime.strptime(start, "%H:%M")
    end_time = datetime.strptime(end, "%H:%M")
    duration = (end_time - start_time).seconds / 3600  # Convertir en heures
    return duration

def parse_time_format(time_str):
    """Convertit différents formats d'horaires en HH:MM."""
    if "h" in time_str:
        time_str = time_str.replace("h", ":")
    if len(time_str) == 4:  # Format HhMM
        time_str = f"0{time_str[:1]}:{time_str[1:]}"
    elif len(time_str) == 5 and time_str[2] != ":":  # Format HHhMM
        time_str = f"{time_str[:2]}:{time_str[3:]}"
    return time_str

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

    # Extraire l'horaire
    try:
        time_range = message.split(" ")[1]
        start, end = time_range.split("-")
        start = parse_time_format(start)
        end = parse_time_format(end)
        hours = calculate_hours(start, end)

        if "current_session" not in user_data[user_id]:
            user_data[user_id]["current_session"] = []

        user_data[user_id]["current_session"].append(f"{start}-{end}")
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

# Ajout des handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("add", add))
app.add_handler(CommandHandler("recap", recap))

# Lancement du bot
if __name__ == "__main__":
    app.run_polling()

