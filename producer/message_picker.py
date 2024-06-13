import logging
import requests
import time
from telegram import Update
from telegram.ext import (
    Application,
    ContextTypes,
    MessageHandler,
)

FLUENT_URL = "http://10.0.100.21:5050"

#Logging configuration

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

ELASTIC_NODE = "http://10.0.100.25:9200"
ELASTIC_PORT = "9200"
ELASTIC_INDEX = "messages"

#Message sender to Fluentd
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = update.message
    if message.text is not None:
        last_message = {"message_id": message.message_id,
                        "text": message.text, 
                        "sender": {"first_name": message.from_user.first_name,
                                "last_name": message.from_user.last_name,
                                "username": message.from_user.username,
                                "sender_id": message.from_user.id}, 
                        "chat": message.chat.effective_name,
                        "chat_user": message.chat.username,
                        "chat_id": message.chat.id, "@timestamp": time.time()}
                
        requests.post(FLUENT_URL, json=last_message, timeout=5) 




def main() -> None:

    application = Application.builder().token("YOUR_TOKEN").build()

    message_handler = MessageHandler(None, handle_message)
    application.add_handler(message_handler)


    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
