from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_DSN = os.getenv("DB_DSN")
GROUP_ID = int(os.getenv("GROUP_ID"))
ADMIN_TELEGRAM_ID = int(os.getenv("ADMIN_TELEGRAM_ID"))
GROUP_INVITE_LINK = os.getenv("GROUP_INVITE_LINK")