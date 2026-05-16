import requests

BOT_TOKEN = "8755768030:AAGK9YAsiqSQcQNjEeApR8F-95uyhuYtl2U"
CHAT_ID = "@fantawrestling_bot"


def send_telegram_message(message):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }

    try:

        requests.post(url, data=data)

    except Exception as e:

        print(e)