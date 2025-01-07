# Commande /recap
async def recap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    lang = get_language(user_id)

    if user_id in user_data and user_data[user_id]["sessions"]:
        total_time = user_data[user_id]["total_time"]
        hours, remainder = divmod(total_time.total_seconds(), 3600)
        minutes = remainder // 60
        await update.message.reply_text(
            f"Total worked time: {int(hours)}h {int(minutes)}min"
        )
    else:
        await update.message.reply_text(LANGUAGES[lang]["no_sessions"])

# Commande /reset
async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    lang = get_language(user_id)

    if user_id in user_data:
        del user_data[user_id]
        await update.message.reply_text(LANGUAGES[lang]["data_reset"])
    else:
        await update.message.reply_text(LANGUAGES[lang]["no_sessions"])

async def export(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    lang = get_language(user_id)

    if user_id not in user_data or not user_data[user_id]["sessions"]:
        await update.message.reply_text(LANGUAGES[lang]["no_sessions"])
        return

    sessions = user_data[user_id]["sessions"]

    try:
        html_content = """<html><head><style>
        table {font-family: Arial, sans-serif; border-collapse: collapse; width: 100%;}
        th, td {border: 1px solid #dddddd; text-align: left; padding: 8px;}
        th {background-color: #f2f2f2;}
        </style></head><body>
        <h2>Work Sessions</h2>
        <table>
        <tr><th>Start</th><th>End</th><th>Worked Time</th></tr>"""

        for arrive_time, depart_time, worked_time in sessions:
            hours, remainder = divmod(worked_time.total_seconds(), 3600)
            minutes = remainder // 60
            html_content += f"<tr><td>{arrive_time}</td><td>{depart_time}</td><td>{int(hours)}h {int(minutes)}min</td></tr>"

        html_content += "</table></body></html>"

        pdf_path = f"work_sessions_{user_id}.pdf"
        pdfkit.from_string(html_content, pdf_path)

        with open(pdf_path, "rb") as pdf_file:
            await update.message.reply_document(document=pdf_file)

    except Exception as e:
        await update.message.reply_text(LANGUAGES[lang]["export_failure"])

# Initialisation du bot
application = Application.builder().token(TOKEN).build()

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("add", add))
application.add_handler(CommandHandler("recap", recap))
application.add_handler(CommandHandler("reset", reset))
application.add_handler(CommandHandler("export", export))

if __name__ == "__main__":
    application.run_polling()

