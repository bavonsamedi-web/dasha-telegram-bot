import random

PHOTOS = [
    "https://i.postimg.cc/BXW8p1sv/IMG-4866.webp",
    "https://i.postimg.cc/tY01kVyJ/IMG-4867.webp",
    "https://i.postimg.cc/tY01kVyC/IMG-4868.webp",
    "https://i.postimg.cc/VdySgb1s/IMG-4869.webp",
    "https://i.postimg.cc/xcrk5bYY/IMG-4870.webp",
    # можешь добавлять остальные по желанию
]

def get_random_photo():
    return random.choice(PHOTOS)
