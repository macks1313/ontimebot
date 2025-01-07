# ontime_bot_with_ai.py
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from transformers import pipeline

# Configurer le journal
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Charger le pipeline GPT-like (sarcastique)
sarcastic_generator = pipeline("text-generation", model="gpt2")

# Gérer la commande /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Salut ! Je suis ontime_bot, ton bot sarcastique boosté à l'IA. Pose-moi une question, et je vais répondre avec mon intelligence supérieure (et un peu de sarcasme). 😏"
    )

# Gérer les messages avec IA
async def respond(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text
    try:
        # Générer une réponse sarcastique avec GPT
        response = sarcastic_generator(
            f"Fais une réponse sarcastique à : {user_message}",
            max_length=50,
            num_return_sequences=1,
        )[0]["generated_text"]
        await update.message.reply_text(response)
    except Exception as e:
        logger.error(f"Erreur dans la génération de texte : {e}")
        await update.message.reply_text(
            "Oups ! Je crois que mon cerveau (d'IA) a eu un problème. Essaye encore !"
        )

# Configuration principale
def main():
    token = "7685304448:AAEuMefo6gvKOydyTtRv6pVXLMxvTuJfWr4"  # Votre token ici

    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, respond))

    app.run_polling()

if __name__ == "__main__":
    main()
