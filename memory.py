conversation_memory = []

def add_message(role, content):
    conversation_memory.append({"role": role, "content": content})

    if len(conversation_memory) > 20:
        conversation_memory.pop(0)

def get_memory():
    return conversation_memory
