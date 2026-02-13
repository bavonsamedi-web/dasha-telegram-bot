import time

def detect_tone(user_message):
    aggressive_words = ["заткнись", "надоела", "бесишь"]
    if any(word in user_message.lower() for word in aggressive_words):
        return "aggressive"
    return "neutral"


def apply_conflict(state, tone):
    if tone == "aggressive":
        state["cooldown_until"] = time.time() + 3600
        state["mood"] = "distant"
    return state
