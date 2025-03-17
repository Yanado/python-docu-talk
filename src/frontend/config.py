import json
import os

import toml
from src.backend.utils.file_io import get_encoded_image, recursive_read

with open(".streamlit/secrets.toml", "r") as file:
    data = toml.load(file)

# Create credentials directory if it doesn't exist
os.makedirs("credentials", exist_ok=True)

# Fix the missing file handle
with open("credentials/gcp_credentials.json", "w") as f:
    if "gcp_credentials" in data:
        # Parse the string as JSON first, then write the resulting object
        if isinstance(data["gcp_credentials"], str):
            try:
                # If it's a JSON string, parse it first
                credential_json = json.loads(data["gcp_credentials"])
                json.dump(credential_json, f, indent=2)
            except json.JSONDecodeError:
                # If parsing fails, write it directly
                f.write(data["gcp_credentials"])
        else:
            # It's already an object
            json.dump(data["gcp_credentials"], f, indent=2)
    else:
        json.dump({}, f)  # Empty JSON object as placeholder

for k, v in data["dotenv"].items():
    os.environ[k] = v

LOGO_PATH = os.path.join(os.path.dirname(__file__), "assets", "logo_docu_talk.png")
ENCODED_LOGO = get_encoded_image(path=LOGO_PATH)
BASE_URL = os.getenv("BASE_URL")

TEXTS = recursive_read(
    folder=os.path.join(os.path.dirname(__file__), "assets", "texts"),
    extensions=(".md")
)

path = os.path.join(os.path.dirname(__file__), "config.json")
with open(path) as f:
    CONFIG = json.load(f)

DISPLAY_GUEST_MODE = CONFIG["display_guest_mode"]
TOKEN_EXPIRATION_HOURS = CONFIG["token_expiration_hours"]
BASIC_MODEL_NAME = CONFIG["models"]["basic"]
PREMIUM_MODEL_NAME = CONFIG["models"]["premium"]
USER_PERIOD_DOLLAR_AMOUNT = CONFIG["credits"]["period_dollar_amount"]["user"]
GUEST_PERIOD_DOLLAR_AMOUNT = CONFIG["credits"]["period_dollar_amount"]["guest"]
CREDIT_EXCHANGE_RATE = CONFIG["credits"]["credit_exchange_rate"]
MAX_ICON_FILE_SIZE = CONFIG["limits"]["max_icon_file_size"]
MAX_NB_DOC_PER_CHATBOT = CONFIG["limits"]["max_nb_doc_per_chatbot"]
MAX_NB_PAGES_PER_CHATBOT = CONFIG["limits"]["max_nb_pages_per_chatbot"]
