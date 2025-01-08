from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import re
import random

# Stockage des données d'heures pour chaque utilisateur
data = {}

# Réponses amusantes
responses = [
    "Oh, te voilà encore ! Prêt à compter tes heures de boulot ? 😏",
    "Toujours en train de travailler, hein ? Ou juste de faire semblant ? 🕒",
    "Salut {user_name}, montre-moi combien tu as bossé aujourd'hui ! 💼",
    "Encore toi, {user_name} ? Tu veux vraiment savoir combien de temps tu as perdu à bosser ? 😂"
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.message.from_user.first_name
    welcome_message = random.choice(responses).format(user_name=user_name)
    await update.message.reply_text(
        f"{welcome_message}\n"
        "👉 Voici les commandes disponibles :\n"
        "• /add <début> <fin> <pause> : Ajoute tes heures (formats acceptés : 8h30, 08:30, 8h).\n"
        "• /reset : Réinitialise toutes tes données. 🚨\n"
        "• /total : Montre le total des heures travaillées. 📊\n"
        "• /info : Affiche une notice détaillée. 📋\n"
        "Alors, prêt(e) à découvrir combien de temps tu perds à bosser ? 💪✨"
    )

def parse_time(time_str):
    """Analyse et convertit les formats d'heures (HHhMM, HH:MM, MM)."""
    time_str = time_str.replace("h", ":")
    parts = time_str.split(":")
    if len(parts) == 1:
        parts.append("00")  # Si seulement "HH" est fourni, ajoutez "00" pour les minutes
    return int(parts[0]), int(parts[1])

def calculate_hours(start: str, end: str, break_minutes: int):
    try:
        start_hours, start_minutes = parse_time(start)
        end_hours, end_minutes = parse_time(end)

        # Validation des valeurs
        if not (0 <= start_hours < 24 and 0 <= start_minutes < 60):
            raise ValueError(f"Heure de début invalide : {start}")
        if not (0 <= end_hours < 24 and 0 <= end_minutes < 60):
            raise ValueError(f"Heure de fin invalide : {end}")

        start_total_minutes = start_hours * 60 + start_minutes
        end_total_minutes = end_hours * 60 + end_minutes

        total_work_minutes = end_total_minutes - start_total_minutes - break_minutes
        if total_work_minutes < 0:
            raise ValueError("Les heures de fin doivent être après les heures de début.")

        work_hours = total_work_minutes // 60
        work_minutes = total_work_minutes % 60

        return work_hours, work_minutes
    except Exception as e:
        raise ValueError(f"Erreur dans le calcul des heures : {str(e)}")

async def handle_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name
    text = " ".join(context.args)

    # Vérifie les arguments
    if len(context.args) != 3:
        await update.message.reply_text(
            f"{user_name}, tu dois entrer trois valeurs : début, fin et pause. Exemple : /add 8h30 19h00 30. 🙄"
        )
        return

    # Vérifie le format des heures
    match = re.match(r"(\d{1,2}[h:]{1}\d{0,2})\s+(\d{1,2}[h:]{1}\d{0,2})\s+(\d+)", text)
    if not match:
        await update.message.reply_text(
            f"{user_name}, format invalide. Utilise : /add 8h30 19h00 30 ou 08:30 19:00 30. Essaie encore ! 😅"
        )
        return

    # Calcule les heures
    start_time, end_time, break_minutes = match.groups()[0], match.groups()[1], match.groups()[2]
    try:
        work_hours, work_minutes = calculate_hours(start_time, end_time, int(break_minutes))
    except ValueError as e:
        await update.message.reply_text(
            f"{user_name}, une erreur est survenue : {str(e)}. Vérifie tes valeurs et réessaie. 🚨"
        )
        return

    # Enregistre les données
    if user_id not in data:
        data[user_id] = 0

    total_minutes = work_hours * 60 + work_minutes
    data[user_id] += total_minutes

    await update.message.reply_text(
        f"Bravo {user_name}, tu as travaillé {work_hours}h et {work_minutes}min aujourd'hui. 🎉\n"
        f"Cumul total : {data[user_id] // 60}h et {data[user_id] % 60}min. Continue comme ça, champion(ne) ! 🙌"
    )

async def reset_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name
    if user_id in data:
        del data[user_id]
        await update.message.reply_text(f"Tout est effacé, {user_name}. N'est-ce pas libérateur ? 🌈")
    else:
        await update.message.reply_text(f"Rien à effacer, {user_name}. T'as rêvé d'avoir travaillé ? 😂")

async def total_hours(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name
    if user_id in data:
        total_minutes = data[user_id]
        await update.message.reply_text(
            f"Depuis le début, tu as accumulé {total_minutes // 60}h et {total_minutes % 60}min. Impressionnant, non {user_name} ? 🤓"
        )
    else:
        await update.message.reply_text(f"Aucune donnée. Tu fais grève, {user_name} ? 😅")

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.message.from_user.first_name
    await update.message.reply_text(
        f"Voici comment utiliser le bot, {user_name} :\n"
        "• /add <début> <fin> <pause> : Ajoute tes heures travaillées.\n"
        "  - Formats acceptés : 8h30, 08:30, 8h (ajout automatique de ':00').\n"
        "  - Exemple : /add 8h30 19h00 30.\n"
        "• /reset : Efface toutes tes données.\n"
        "• /total : Affiche le total cumulé depuis la dernière réinitialisation.\n"
        "• /info : Affiche cette notice détaillée.\n"
        "Voilà, simple et efficace, non ? 🚀"
    )

def main():
    bot_token = "7685304448:AAEuMefo6gvKOydyTtRv6pVXLMxvTuJfWr4"
    application = Application.builder().token(bot_token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add", handle_add))
    application.add_handler(CommandHandler("reset", reset_data))
    application.add_handler(CommandHandler("total", total_hours))
    application.add_handler(CommandHandler("info", info))

    application.run_polling()

if __name__ == "__main__":
    main()
