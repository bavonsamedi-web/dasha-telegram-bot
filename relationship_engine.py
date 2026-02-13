import time

def update_relationship(state, user_message):

    lower = user_message.lower()

    if any(word in lower for word in ["люблю", "важна", "дорога"]):
        state["relationship"] += 2

    if any(word in lower for word in ["игнор", "пофиг", "отстань"]):
        state["relationship"] -= 3
        state["cooldown_until"] = time.time() + 1800  # 30 мин дистанции

    # стадии
    if state["relationship"] < 30:
        state["stage"] = "early"
    elif state["relationship"] < 70:
        state["stage"] = "attached"
    else:
        state["stage"] = "deep"

    return state
