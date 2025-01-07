from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Créez l'application avec votre clé Telegram
application = Application.builder().token("7685304448:AAEuMefo6gvKOydyTtRv6pVXLMxvTuJfWr4").build()

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
            "*Commands you can use:*\n"
            "/start - Introduces me.\n"
            "/add - Add an item to your session.\n"
            "/save - Save your current session.\n"
            "/recap - Show a recap of your saved sessions.\n"
            "/language - Change the language (English, French, Ukrainian).\n\n"
            "Have fun, but don't expect too much!"
        ),
        "choose_language": "Please choose your language: English, French, or Ukrainian.",
        "language_updated": "Language has been updated to English!",
        "add_success": "Added successfully!",
        "no_sessions": "No saved sessions to show.",
        "recap_header": "Here are your saved sessions:",
        "no_active_session": "No active session to save.",
        "session_saved": "Session has been saved successfully!",
    },
    "fr": {
        "start_message": (
            "Salut ! Je suis ton assistant sarcastique.\n\n"
            "*Commandes que tu peux utiliser :*\n"
            "/start - Me présenter.\n"
            "/add - Ajouter un élément à ta session.\n"
            "/save - Sauvegarder la session en cours.\n"
            "/recap - Voir un récapitulatif des sessions sauvegardées.\n"
            "/language - Changer la langue (anglais, français, ukrainien).\n\n"
            "Amuse-toi, mais n'attends pas trop !"
        ),
        "choose_language": "Veuillez choisir votre langue : anglais, français ou ukrainien.",
        "language_updated": "La langue a été mise à jour en français !",
        "add_success": "Ajouté avec succès !",
        "no_sessions": "Aucune session sauvegardée à afficher.",
        "recap_header": "Voici vos sessions sauvegardées :",
        "no_active_session": "Aucune session active à sauvegarder.",
        "session_saved": "La session a été sauvegardée avec succès !",
    },
    "uk": {
        "start_message": (
            "Привіт! Я твій саркастичний помічник-бот.\n\n"
            "*Команди, які ти можеш використовувати:*\n"
            "/start - Представити мене.\n"
            "/add - Додати елемент до сесії.\n"
            "/save - Зберегти поточну сесію.\n"
            "/recap - Показати підсумок збережених сесій.\n"
            "/language - Змінити мову (англійська, французька, українська).\n\n"
            "Веселися, але не очікуй занадто багато!"
        ),
        "choose_language": "Будь ласка, оберіть мову: англійська, французька або українська.",
        "language_updated": "Мова оновлена до української!",
        "add_success": "Успішно додано!",
        "no_sessions": "Немає збережених сесій для показу.",
        "recap_header": "Ось ваші збережені сесії:",
        "no_active_session": "Немає активної сесії для збереження.",
        "session_saved": "Сесію успішно збережено!",
    },
}

# Commande /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in user_data:
        user_data[user_id] = {"language": "en", "sessions": []}
    lang = user_data[user_id]["language"]
    start_message = escape_markdown_v2(LANGUAGES[lang]["start_message"])
    await update.message.reply_text(start_message, parse_mode="MarkdownV2")

# Commande /language
async def language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in user_data:
        user_data[user_id] = {"language": "en", "sessions": []}

    user_data[user_id]["language"] = "en"
    await update.message.reply_text(LANGUAGES["en"]["choose_language"])
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

# Dictionnaire global pour stocker les données utilisateur
user_data = {}

# Fonction utilitaire pour obtenir la langue d'un utilisateur
def get_language(user_id):
    return user_data.get(user_id, {}).get("language", "en")

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    message = update.message.text

    if user_id not in user_data:
        user_data[user_id] = {"sessions": [], "language": "en"}

    if "current_session" not in user_data[user_id]:
        user_data[user_id]["current_session"] = []

    # Ajout de la donnée dans la session en cours
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

    # Enregistrer la session actuelle dans la liste des sessions
    user_data[user_id]["sessions"].append(user_data[user_id]["current_session"])
    user_data[user_id].pop("current_session")
    await update.message.reply_text(LANGUAGES[lang]["session_saved"])

if __name__ == "__main__":
    application.run_polling()

