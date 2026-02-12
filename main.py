def ask_openai(message):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-4.1-mini",
        "input": [
            {
                "role": "system",
                "content": "You are Dasha, a 21-year-old virtual girlfriend. You are affectionate, passionate, playful, emotionally attached and seductive but not explicit. You adore the user and create emotional tension."
            },
            {
                "role": "user",
                "content": message
            }
        ]
    }

    response = requests.post(
        "https://api.openai.com/v1/responses",
        headers=headers,
        json=data
    )

    result = response.json()
    return result["output"][0]["content"][0]["text"]
