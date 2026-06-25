"""
In-memory game state per team (keyed by WhatsApp number).
Resets if the server restarts – fine for single-day events.
For multi-day events, swap the dict for a JSON file or SQLite.
"""

teams = {}   # { "whatsapp:+91XXXXXXXXXX": TeamState }


class TeamState:
    def __init__(self, phone: str):
        self.phone           = phone
        self.name            = None       # set after registration
        self.current_clue    = 1          # starts at challenge 1
        self.score           = 0
        self.completed       = []         # list of completed challenge ids
        self.registered      = False
        self.waiting_for     = None       # e.g. "team_name"
        self.message_history = []         # last N messages for context


def get_or_create(phone: str) -> TeamState:
    if phone not in teams:
        teams[phone] = TeamState(phone)
    return teams[phone]


def all_teams_summary() -> list[dict]:
    return [
        {
            "name":      t.name or t.phone,
            "phone":     t.phone,
            "score":     t.score,
            "completed": len(t.completed),
        }
        for t in sorted(teams.values(), key=lambda x: x.score, reverse=True)
    ]
