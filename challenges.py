# ============================================================
#  SAMPLE CHALLENGES  –  edit freely
#  Each challenge has:
#    id        : unique number
#    clue      : dramatic text sent to the team
#    task      : what they must do
#    type      : "photo" | "text" | "location"
#    validate  : what AI looks for in the photo (for photo tasks)
#    points    : score awarded on success
#    hint      : hint if team asks for help
# ============================================================

CHALLENGES = [
    {
        "id": 1,
        "clue": (
            "🕵️ *MISSION BRIEFING – CHECKPOINT 1*\n\n"
            "Agent, your first target is a *RED vehicle*.\n"
            "Find one, photograph it, and send proof.\n"
            "Time is ticking. Go."
        ),
        "task": "Send a photo of a red vehicle.",
        "type": "photo",
        "validate": "Is there a red coloured vehicle (car, bike, truck, bus, etc.) clearly visible in this image?",
        "points": 50,
        "hint": "Look in the nearest parking area or road.",
    },
    {
        "id": 2,
        "clue": (
            "🔥 *CHECKPOINT 2 UNLOCKED*\n\n"
            "Well done, Agent.\n"
            "Next: Find a *fire extinguisher* inside any building.\n"
            "Photograph it and report back."
        ),
        "task": "Send a photo of a fire extinguisher.",
        "type": "photo",
        "validate": "Is there a fire extinguisher (red cylinder safety device) visible in this image?",
        "points": 60,
        "hint": "Check near staircases, corridors, or building entrances.",
    },
    {
        "id": 3,
        "clue": (
            "📸 *CHECKPOINT 3 – TEAM POWER*\n\n"
            "Agents, now show your strength.\n"
            "Send a *team selfie* with ALL members visible.\n"
            "Together you are stronger."
        ),
        "task": "Send a group selfie with all team members.",
        "type": "photo",
        "validate": "Are there multiple people (2 or more) taking a selfie or group photo together?",
        "points": 70,
        "hint": "Find a spot with good light and fit everyone in the frame.",
    },
    {
        "id": 4,
        "clue": (
            "🔒 *CHECKPOINT 4 – THE GUARDIAN*\n\n"
            "Somewhere nearby, a guardian watches over.\n"
            "Find a *security guard* and photograph them.\n"
            "Respect is mandatory."
        ),
        "task": "Send a photo of a security guard (with their permission).",
        "type": "photo",
        "validate": "Is there a person in a security guard uniform or wearing a security badge visible in this image?",
        "points": 80,
        "hint": "Check building entrances, reception areas, or parking lots.",
    },
    {
        "id": 5,
        "clue": (
            "🏆 *FINAL CHECKPOINT – THE LOGO*\n\n"
            "Agent, the end is near.\n"
            "Find and photograph your *company logo* — "
            "on a wall, banner, letterhead, or signboard.\n"
            "Claim your victory."
        ),
        "task": "Send a photo of the company logo.",
        "type": "photo",
        "validate": "Is there a company logo, brand signage, or corporate branding visible in this image?",
        "points": 100,
        "hint": "Check the reception wall, entrance banner, or any official material.",
    },
]

# Quick lookup by challenge id
CHALLENGE_MAP = {c["id"]: c for c in CHALLENGES}
TOTAL_CHALLENGES = len(CHALLENGES)
