import os
import requests
from datetime import datetime
import pytz
from dotenv import load_dotenv

# load environment variables from .env file
dotenv_path = os.path.join(os.path.dirname(__file__), "..", ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

TRELLO_KEY = os.getenv("TRELLO_KEY")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN")
TRELLO_LIST_ID = os.getenv("TRELLO_LIST_ID")

def add_card_to_trello(title, username="Unknown"):
    """
        Adds a card to Trello containing the text, sender’s name, and timestamp.
    """
    cairo_time = datetime.now(pytz.timezone("Africa/Cairo")).strftime("%Y-%m-%d %H:%M:%S")

    card_name = f"{title.strip()}"
    description = f" sender: {username}\n time: {cairo_time}"

    url = "https://api.trello.com/1/cards"
    query = {
        "idList": TRELLO_LIST_ID,
        "key": TRELLO_KEY,
        "token": TRELLO_TOKEN,
        "name": card_name,
        "desc": description
    }

    response = requests.post(url, params=query)
    if response.status_code == 200:
        return f"added by {username}"
    else:
        print("Trello Error:", response.text)
        print("DEBUG:", query)
        return "Error during adding to Trello"