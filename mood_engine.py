import random
import time

def update_mood(state):

    # если в охлаждении — distant
    if state["cooldown_until"] > time.time():
        state["mood"] = "distant"
        return state

    roll = random.random()

    if roll < 0.2:
        state["mood"] = "playful"
    elif roll < 0.4:
        state["mood"] = "warm"
    elif roll < 0.6:
        state["mood"] = "calm"
    elif roll < 0.8:
        state["mood"] = "focused"
    else:
        state["mood"] = "slightly_distant"

    return state
