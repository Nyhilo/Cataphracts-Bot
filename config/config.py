import os
from dotenv import load_dotenv
load_dotenv()

DEBUG = os.getenv('DEBUG') == 'TRUE'

# Discord API related stuff #
PREFIX = '&'

LOG_FILE = 'log.txt'

MESSAGE_LIMIT = 2000
LINE_SPLIT_LIMIT = 200

# This is set to false to prevent cheating when secretly generating a Sha265
LOG_DEBUG_TO_FILE = True if DEBUG else False

SQLITE3_DB_NAME = 'sqlite3.db'
DB_TABLE_REMINDERS_NAME = 'Reminders'
DB_TABLE_POOLS_NAME = 'Pools'
DB_TABLE_POOL_ENTRIES_NAME = 'Pool_Entries'
DB_TABLE_SETTINGS_NAME = 'Settings'

GLOBAL_ADMIN_IDS = [116698920515534854]
SERVER_ADMIN_IDS = {
    # Cataphract
    1390018254273118318: [
        499526890869096449
    ]
}

QUICK_REMIND_SECONDS_THRESHOLD = 60 * 10

# Voice channels for time-tracking updates
UTC_UPDATE_CHANNEL = 1390018254726238406 if not DEBUG else 443181366184640517
