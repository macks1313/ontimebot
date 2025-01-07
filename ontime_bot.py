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
    "en": {
        "start_message": (
            "Hello! I'm your sarcastic assistant bot.\n\n"
            "Here are the commands I understand:\n"
            "/start - Starts me, of course.\n"
            "/help - Shows this fabulous list of commands.\n"
            "/language - Change my language (English, French, Ukrainian).\n"
            "/add - Add working hours (format: HH:MM-HH:MM).\n"
            "/recap - Get a summary of your saved sessions.\n"
            "/save_session - Save the current session.\n\n"
            "What do you want now? 🤔"
        ),
        "add_success": "Fine, I've added that to your session. Total hours worked so far: {hours:.2f} hours.",
        "invalid_format": "I couldn't understand the time format. Please use HH:MM-HH:MM.",
    },
    "fr": {
        "start_message": (
            "Bonjour ! Je suis votre assistant sarcastique.\n\n"
            "Voici les commandes que je comprends :\n"
            "/start - Me démarrer, bien sûr.\n"
            "/help - Montre cette liste fabuleuse de commandes.\n"
            "/language - Change ma langue (Anglais, Français, Ukrainien).\n"
            "/add - Ajouter des horaires de travail (format : HH:MM-HH:MM).\n"
            "/recap - Obtenir un résumé de vos sessions enregistrées.\n"
            "/save_session - Enregistrer la session actuelle.\n\n"
            "Et maintenant, qu'est-ce que tu veux ? 🤔"
        ),
        "add_success": "Très bien, j'ai ajouté ça à votre session. Heures totales travaillées : {hours:.2f} heures.",
        "invalid_format": "Je n'ai pas compris le format. Utilisez HH:MM-HH:MM.",
    },
    "uk": {
        "start_message": (
            "Привіт! Я ваш саркастичний асистент бот.\n\n"
            "Ось команди, які я розумію:\n"
            "/start - Запустити мене, звісно.\n"
            "/help - Показати цей фантастичний список команд.\n"
            "/language - Змінити мою мову (Англійська, Французька, Українська).\n"
            "/add - Додати години роботи (формат: HH:MM-HH:MM).\n"
            "/recap - Отримати резюме ваших збережених сесій.\n"
            "/save_session - Зберегти поточну сесію.\n\n"
            "І що тепер? 🤔"
        ),
        "add_success": "Добре, я додав це до вашої сесії. Загальна кількість годин: {hours:.2f} год.",
        "invalid_format": "Я не зрозумів формат. Використовуйте HH:MM-HH:MM.",
    },
}
from datetime import datetime

# Fonction pour obtenir la langue d'un utilisateur
user_data = {}

def get_language(user_id):
    return user_data.get(user_id, {}).get("language", "en")

def calculate_hours(start, end):
    """Calcule les heures entre deux horaires."""
    start_time = datetime.strptime(start, "%H:%M")
    end_time = datetime.strptime(end, "%H:%M")
    duration = (end_time - start_time).seconds / 3600  # Convertir en heures
    return duration

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_data[user_id] = {"sessions": [], "language": "en", "total_hours": 0}
    lang = get_language(user_id)
    await update.message.reply_text(LANGUAGES[lang]["start_message"])

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    lang = get_language(user_id)
    message = update.message.text

    if user_id not in user_data:
        user_data[user_id] = {"sessions": [], "language": "en", "total_hours": 0}

    # Extraire l'horaire
    try:
        time_range = message.split(" ")[1]
        start, end = time_range.split("-")
        hours = calculate_hours(start, end)

        if "current_session" not in user_data[user_id]:
            user_data[user_id]["current_session"] = []

        user_data[user_id]["current_session"].append(f"{start}-{end}")
        user_data[user_id]["total_hours"] += hours

        await update.message.reply_text(
            LANGUAGES[lang]["add_success"].format(hours=user_data[user_id]["total_hours"])
        )
    except (ValueError, IndexError):
        await update.message.reply_text(LANGUAGES[lang]["invalid_format"])

async def recap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    lang = get_language(user_id)

    if user_id not in user_data or "sessions" not in user_data[user_id] or not user_data[user_id]["sessions"]:
        await update.message.reply_text("No sessions recorded.")
        return

    recap_message = "Here is your recap:\n"
    for session in user_data[user_id]["sessions"]:
        recap_message += f"- {session}\n"

    await update.message.reply_text(recap_message)

# Ajout des handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("add", add))
app.add_handler(CommandHandler("recap", recap))

# Lancement du bot
if __name__ == "__main__":
    app.run_polling()

