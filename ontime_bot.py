# Partie A : Initialisation et gestion des commandes principales

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Votre TOKEN ici
TOKEN = "7685304448:AAEuMefo6gvKOydyTtRv6pVXLMxvTuJfWr4"

# Langues disponibles
LANGUAGES = {
    "en": {
        "start_message": (
            "Oh, great, another human trying to be productive. Welcome! Here are the things I *begrudgingly* do:\n\n"
            "- /add [text]: Add something to your current session. I won't judge.\n"
            "- /recap: Get a recap of your sessions so far. Spoiler: They're amazing, right?\n"
            "- /save: Save your current session. Because, you know, memories.\n"
            "- /set_language [en/fr/uk]: Change my language.\n"
        ),
        "help_message": "Need help? Typical. Here's what I do:\n/add, /recap, /save, /set_language. Try them.",
        "add_success": "Added. Because your input is *so* valuable.",
        "no_sessions": "No sessions? Wow, productive much?",
        "recap_header": "Here's your recap. Prepare to be amazed:",
        "no_active_session": "No active session. What are you even doing?",
        "session_saved": "Session saved. You're welcome.",
        "language_set": "Language set to English.",
    },
    "fr": {
        "start_message": (
            "Oh, génial, encore un humain qui veut être productif. Bienvenue ! Voici ce que je *supporte* de faire :\n\n"
            "- /add [texte] : Ajoute quelque chose à votre session en cours. Aucun jugement.\n"
            "- /recap : Obtenez un récapitulatif de vos sessions. Spoiler : elles sont incroyables, non ?\n"
            "- /save : Sauvegardez votre session actuelle. Parce que, vous savez, les souvenirs.\n"
            "- /set_language [en/fr/uk] : Changez ma langue.\n"
        ),
        "help_message": "Besoin d'aide ? Classique. Voici ce que je fais :\n/add, /recap, /save, /set_language. Essayez-les.",
        "add_success": "Ajouté. Parce que votre saisie est *tellement* précieuse.",
        "no_sessions": "Aucune session ? Impressionnant de productivité.",
        "recap_header": "Voici votre récapitulatif. Préparez-vous à être émerveillé :",
        "no_active_session": "Aucune session active. Qu'est-ce que vous faites ?",
        "session_saved": "Session sauvegardée. De rien.",
        "language_set": "Langue définie sur le français.",
    },
    "uk": {
        "start_message": (
            "О, чудово, ще одна людина намагається бути продуктивною. Ласкаво просимо! Ось, що я *вимушено* роблю:\n\n"
            "- /add [текст]: Додає щось до вашої поточної сесії. Без суджень.\n"
            "- /recap: Отримайте огляд ваших сесій. Спойлер: вони чудові, правда?\n"
            "- /save: Збережіть свою поточну сесію. Тому що, знаєте, спогади.\n"
            "- /set_language [en/fr/uk]: Змініть мою мову.\n"
        ),
        "help_message": "Потрібна допомога? Очікувано. Ось що я роблю:\n/add, /recap, /save, /set_language. Спробуйте.",
        "add_success": "Додано. Бо ваш внесок *такий* цінний.",
        "no_sessions": "Немає сесій? Вау, продуктивно.",
        "recap_header": "Ось ваш огляд. Готуйтеся до здивувань:",
        "no_active_session": "Немає активної сесії. Що ви робите?",
        "session_saved": "Сесію збережено. Не дякуйте.",
        "language_set": "Мову змінено на українську.",
    },
}

# Dictionnaire global pour stocker les données utilisateur
user_data = {}

# Fonction utilitaire pour obtenir la langue de l'utilisateur
def get_language(user_id):
    return user_data.get(user_id, {}).get("language", "en")

# Commande /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_data[user_id] = {"sessions": [], "language": "en"}
    lang = get_language(user_id)
    await update.message.reply_text(LANGUAGES[lang]["start_message"], parse_mode="Markdown")

# Commande pour changer de langue
async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    lang_code = context.args[0] if context.args else "en"

    if lang_code in LANGUAGES:
        user_data[user_id]["language"] = lang_code
        await update.message.reply_text(LANGUAGES[lang_code]["language_set"])
    else:
        await update.message.reply_text("Language not supported. Try: en, fr, uk.")

# Partie B : Commandes pour gérer les sessions et les récapitulatifs

# Commande /add
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

# Commande /recap
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

# Commande /save
async def save_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    lang = get_language(user_id)

    if user_id not in user_data or "current_session" not in user_data[user_id]:
        await update.message.reply_text(LANGUAGES[lang]["no_active_session"])
        return

    # Enregistrer la session actuelle
    user_data[user_id]["sessions"].append(user_data[user_id]["current_session"])
    user_data[user_id].pop("current_session")
    await update.message.reply_text(LANGUAGES[lang]["session_saved"])

# Ajout des handlers
def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("set_language", set_language))
    application.add_handler(CommandHandler("add", add))
    application.add_handler(CommandHandler("recap", recap))
    application.add_handler(CommandHandler("save", save_session))

    print("Bot is running... sarcastically.")
    application.run_polling()

if __name__ == "__main__":
    main()
