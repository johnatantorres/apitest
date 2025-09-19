import sys
import os


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.chat.schemas import Preferences
from app.chat.tools import check_odds_by_dates_sync

# The tool functions rely on a sport_id being set in the Preferences.
# In the main application, this is handled by the initiate_chat_service.
# For this test script, we need to set it manually.
Preferences.sport_id = 1  # Assuming 1 is a valid sport ID.

check_odds_by_dates_sync("2025-09-20", "2025-09-21")