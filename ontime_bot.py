from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from datetime import datetime, timedelta
import re

# Remplacez "YOUR_TOKEN" par votre clé API de BotFather
import os
TOKEN = os.getenv("TOKEN")

# Dictionnaire pour stocker les données utilisateur
user_data = {}

# Fonction pour parser les heures dans différents formats
def parse_time(time_str):
    try:
        # Supporte les formats comme 08h30, 8:30am, 20:30
        time_str = time_str.replace("h", ":").lower()
        if "am" in time_str or "pm" in time_str:
            return datetime.strptime(time_str, "%I:%M%p").time()
        else:
            return datetime.strptime(time_str, "%H:%M").time()
    except ValueError:
        raise ValueError("Format d'heure invalide")

# Commande /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🙄 **Bienvenue sur OnTime Bot** \n\n"
        "🎉 Sérieusement, vous ne pouvez pas gérer vos heures vous-même ?\n\n"
        "📌 **Commandes disponibles** :\n"
        "🕒 /add arrivée départ - Enregistrer une session (exemple : /add 08h30 17h30 ou /add 8:30am 5:00pm)\n"
        "📊 /recap - Voir combien de temps vous avez prétendu travailler\n"
        "🗑 /reset - Effacer vos données (comme si elles étaient importantes).\n\n"
        "🤖 Faites-moi travailler pour vous, c'est ce que je fais de mieux !"
    )

# Commande /add
async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if len(context.args) != 2:
        await update.message.reply_text(
            "⚠️ **Format incorrect !** \n\n"
            "✏️ Utilisez : /add arrivée départ (exemple : /add 08h30 17h30 ou /add 8:30am 5:00pm). \n"
            "Ce n'est pas si compliqué, si ? 🤔"
        )
        return

    try:
        arrive_time = parse_time(context.args[0])
        depart_time = parse_time(context.args[1])

        arrive_datetime = datetime.combine(datetime.today(), arrive_time)
        depart_datetime = datetime.combine(datetime.today(), depart_time)

        if depart_datetime <= arrive_datetime:
            await update.message.reply_text(
                "⚠️ **Erreur temporelle** \n\n"
                "🕰️ L'heure de départ doit être après l'heure d'arrivée. Vous n'êtes pas encore un voyageur temporel, à ce que je sache."
            )
            return

        worked_time = depart_datetime - arrive_datetime

        if user_id not in user_data:
            user_data[user_id] = {"sessions": [], "total_time": timedelta()}

        user_data[user_id]["sessions"].append((arrive_time, depart_time, worked_time))
        user_data[user_id]["total_time"] += worked_time

        hours, remainder = divmod(worked_time.total_seconds(), 3600)
        minutes = remainder // 60
        await update.message.reply_text(
            f"✅ **Session enregistrée !** \n\n"
            f"🕒 **Arrivée** : {arrive_time} \n"
            f"🏁 **Départ** : {depart_time} \n"
            f"⏱ **Temps travaillé** : {int(hours)}h {int(minutes)}min \n\n"
            "💪 Impressionnant, non ? Enfin, si on peut appeler ça du travail."
        )
    except ValueError:
        await update.message.reply_text(
            "⚠️ **Format invalide** \n\n"
            "Essayez quelque chose comme 08h30, 8:30am, ou 17:30. \n"
            "Ce n'est pas sorcier ! 🪄"
        )

# Commande /recap
async def recap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id in user_data and user_data[user_id]["sessions"]:
        total_time = user_data[user_id]["total_time"]
        hours, remainder = divmod(total_time.total_seconds(), 3600)
        minutes = remainder // 60
        await update.message.reply_text(
            f"📊 **Récapitulatif** \n\n"
            f"🔢 Total travaillé depuis la dernière réinitialisation : \n"
            f"⏱ **{int(hours)}h {int(minutes)}min** \n\n"
            "👏 Bravo pour vos efforts... ou pour avoir trompé le système."
        )
    else:
        await update.message.reply_text(
            "❌ **Aucune session enregistrée** \n\n"
            "🙃 Peut-être que vous n'avez rien fait ? \n"
            "Essayez /add pour commencer !"
        )

# Commande /reset
async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id in user_data:
        del user_data[user_id]
        await update.message.reply_text(
            "🗑️ **Données réinitialisées** \n\n"
            "📂 Vous repartez de zéro ! Parfois, il faut tout recommencer, surtout avec vous. 😏"
        )
    else:
        await update.message.reply_text(
            "❌ **Rien à réinitialiser** \n\n"
            "Sérieusement, vous n'avez encore rien fait. 🤷‍♂️"
        )

# Configuration principale
def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add", add))
    application.add_handler(CommandHandler("recap", recap))
    application.add_handler(CommandHandler("reset", reset))

    application.run_polling()

if __name__ == "__main__":
    main()
