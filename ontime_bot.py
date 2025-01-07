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

# Dictionnaire des messages sarcastiques en plusieurs langues
LANGUAGES = {
    "fr": {
        "start_message": (
            "✨ Bonjour {name} !\n\n"
            "Je suis ton assistant bot 🤖, prêt à… enfin… me débrouiller pour suivre tes horaires de travail, car apparemment tu ne peux pas le faire toi-même. 😏\n\n"
            "Voici ce que je peux faire pour toi :\n"
            "/start - Me démarrer. Bravo, tu viens déjà de le faire.\n"
            "/add - Ajouter des horaires (formats acceptés : HH:MM, HHhMM, HhMM).\n"
            "/recap - Obtenir un magnifique récapitulatif de ton labeur épique.\n"
            "/delete - Supprimer toutes tes données, comme si je n’avais jamais existé. 🙃\n"
            "/language - Changer ma langue (Anglais, Français, Ukrainien).\n\n"
            "Maintenant, dis-moi, ô maître, que puis-je faire pour toi aujourd'hui ? 😎"
        ),
        "add_success": (
            "✨ Très bien {name}, j'ai ajouté ça à ta session. Total d'heures travaillées : {hours:.2f} heures.\n\n"
            "Tu progresses, petit génie. Continue comme ça. 🤓"
        ),
        "invalid_format": "Euh… pardon ? Ce format est incompréhensible. Essaie : HH:MM, HHhMM ou HhMM. 🧐",
        "no_sessions": "Tu n'as enregistré aucune session. Félicitations pour ton inactivité. 👏",
        "recap_header": "📋 Voici un récapitulatif de tes sessions de travail incroyablement inspirantes :\n",
        "data_deleted": "🚮 Toutes tes données ont été supprimées. J'espère que c'était intentionnel. 🙄",
    },
    "en": {
        "start_message": (
            "✨ Hello {name}!\n\n"
            "I'm your assistant bot 🤖, here to… well… try my best to track your working hours, since you clearly can't. 😏\n\n"
            "Here’s what I can do for you:\n"
            "/start - Start me. Congrats, you've already done it.\n"
            "/add - Add working hours (formats accepted: HH:MM, HHhMM, HhMM).\n"
            "/recap - Get a wonderful summary of your epic labor.\n"
            "/delete - Erase all your data, like I never existed. 🙃\n"
            "/language - Change my language (English, French, Ukrainian).\n\n"
            "So, tell me, oh master, what can I do for you today? 😎"
        ),
        "add_success": (
            "✨ Alright {name}, I’ve added that to your session. Total hours worked: {hours:.2f} hours.\n\n"
            "You're doing great, Einstein. Keep it up. 🤓"
        ),
        "invalid_format": "Uh… sorry? That format makes no sense. Try: HH:MM, HHhMM, or HhMM. 🧐",
        "no_sessions": "You haven’t recorded any sessions. Congrats on your inactivity. 👏",
        "recap_header": "📋 Here’s a summary of your incredibly inspiring work sessions:\n",
        "data_deleted": "🚮 All your data has been deleted. I hope that was intentional. 🙄",
    },
    "uk": {
        "start_message": (
            "✨ Привіт {name}!\n\n"
            "Я твій бот-асистент 🤖, який допоможе відстежувати твої години роботи, бо ти сам цього не можеш, так? 😏\n\n"
            "Ось що я можу зробити для тебе:\n"
            "/start - Запустити мене. Вітаю, ти вже це зробив.\n"
            "/add - Додати години роботи (формати: HH:MM, HHhMM, HhMM).\n"
            "/recap - Отримати чудове зведення твоєї епічної праці.\n"
            "/delete - Видалити всі твої дані, ніби мене ніколи не було. 🙃\n"
            "/language - Змінити мову (Англійська, Французька, Українська).\n\n"
            "Ну що, командуй, мій господарю. Що я можу зробити для тебе сьогодні? 😎"
        ),
        "add_success": (
            "✨ Добре, {name}, я додав це до твоєї сесії. Загальна кількість годин: {hours:.2f} год.\n\n"
            "Молодець, генію. Продовжуй у тому ж дусі. 🤓"
        ),
        "invalid_format": "Емм… вибачте? Цей формат незрозумілий. Спробуйте: HH:MM, HHhMM або HhMM. 🧐",
        "no_sessions": "Ти ще не записав жодної сесії. Вітаю з бездіяльністю. 👏",
        "recap_header": "📋 Ось підсумок твоїх неймовірно надихаючих робочих сесій:\n",
        "data_deleted": "🚮 Всі твої дані були видалені. Сподіваюся, це було навмисно. 🙄",
    },
}
from datetime import datetime

# Gestion des données utilisateur
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

    try:
        time_range = message.split(" ")[1]
        start, end = time_range.split("-")
        start = parse_time_format(start)
        end = parse_time_format(end)
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
