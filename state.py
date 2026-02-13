import time

state = {
    "mood": "calm",
    "relationship_level": 30,
    "last_user_message_time": time.time(),
    "last_bot_message_time": 0
}

def get_state():
    return state

def update_last_user_time():
    state["last_user_message_time"] = time.time()

def update_mood(new_mood):
    state["mood"] = new_mood

def increase_relationship(value=1):
    state["relationship_level"] += value

def decrease_relationship(value=1):
    state["relationship_level"] -= value
