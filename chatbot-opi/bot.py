from telegram.ext import Application, CommandHandler, MessageHandler, filters
from handlers import start, handle_message

TOKEN = "7610990305:AAFOPtaA1ed2GPHg24iybvnJ20BhJc70F3M"

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()