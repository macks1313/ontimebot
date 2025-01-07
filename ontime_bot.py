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
            "/add - Add something to your current session.\n"
            "/recap - Get a summary of your saved sessions.\n"
            "/save_session - Save the current session.\n\n"
            "What do you want now? 🤔"
        ),
        "help_message": "Here are the things I can do. It's not much, but it's honest work.",
        "add_success": "Fine, I've added that to your session.",
        "no_sessions": "You have no sessions saved. Do I look like a mind reader?",
        "recap_header": "Here’s your session recap:",
        "no_active_session": "There’s no active session to save. Are you lost?",
        "session_saved": "Your session has been saved. Finally."
    },
    "fr": {
        "start_message": (
            "Bonjour ! Je suis votre assistant sarcastique.\n\n"
            "Voici les commandes que je comprends :\n"
            "/start - Me démarrer, bien sûr.\n"
            "/help - Montre cette liste fabuleuse de commandes.\n"
            "/language - Change ma langue (Anglais, Français, Ukrainien).\n"
            "/add - Ajouter quelque chose à votre session actuelle.\n"
            "/recap - Obtenir un résumé de vos sessions enregistrées.\n"
            "/save_session - Enregistrer la session actuelle.\n\n"
            "Et maintenant, qu'est-ce que tu veux ? 🤔"
        ),
        "help_message": "Voici ce que je peux faire. Ce n'est pas beaucoup, mais c'est honnête.",
        "add_success": "Très bien, j'ai ajouté ça à votre session.",
        "no_sessions": "Vous n'avez aucune session enregistrée. Je ne lis pas dans les pensées.",
        "recap_header": "Voici un résumé de vos sessions :",
        "no_active_session": "Il n'y a pas de session active à enregistrer. Vous êtes perdu ?",
        "session_saved": "Votre session a été enregistrée. Enfin."
    },
    "uk": {
        "start_message": (
            "Привіт! Я ваш саркастичний асистент бот.\n\n"
            "Ось команди, які я розумію:\n"
            "/start - Запустити мене, звісно.\n"
            "/help - Показати цей фантастичний список команд.\n"
            "/language - Змінити мою мову (Англійська, Французька, Українська).\n"
            "/add - Додати щось до вашої поточної сесії.\n"
            "/recap - Отримати резюме ваших збережених сесій.\n"
            "/save_session - Зберегти поточну сесію.\n\n"
            "І що тепер? 🤔"
        ),
        "help_message": "Ось що я можу зробити. Не багато, але чесно.",
        "add_success": "Добре, я додав це до вашої сесії.",
        "no_sessions": "У вас немає збережених сесій. Ви ворожбит?",
        "recap_header": "Ось резюме ваших сесій:",
        "no_active_session": "Немає активної сесії для збереження. Ви загубилися?",
        "session_saved": "Вашу сесію збережено. Нарешті."
    },
}
# Fonction pour obtenir la langue d'un utilisateur
user_data = {}

def get_language(user_id):
    return user_data.get(user_id, {}).get("language", "en")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_data[user_id] = {"language": "en"}
    lang = get_language(user_id)
    await update.message.reply_text(LANGUAGES[lang]["start_message"])

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_language(update.message.from_user.id)
    await update.message.reply_text(LANGUAGES[lang]["help_message"])

async def language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text.split()

    if len(text) == 2 and text[1].lower() in LANGUAGES:
        user_data[user_id]["language"] = text[1].lower()
        await update.message.reply_text(f"Language switched to {text[1]}.")
    else:
        await update.message.reply_text("Please specify a valid language: en, fr, uk.")

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
app.add_handler(CommandHandler("language", language))
app.add_handler(CommandHandler("add", add))
app.add_handler(CommandHandler("recap", recap))
app.add_handler(CommandHandler("save_session", save_session))

# Lancement du bot
if __name__ == "__main__":
    app.run_polling()
