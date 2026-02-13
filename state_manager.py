import json
import time

STATE_FILE = "state.json"

DEFAULT_STATE = {
    "relationship": 20,
    "stage": "early",
    "mood": "calm",
    "last_user_message": time.time(),
    "last_bot_message": 0,
    "cooldown_until": 0
}


def load_state():
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except:
        return DEFAULT_STATE.copy()


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)
