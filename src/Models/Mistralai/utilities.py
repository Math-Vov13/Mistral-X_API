from mistralai import Mistral
from os import environ as env

model = Mistral(
        api_key= env["MISTRAL_API_KEY"],
        server_url="https://api.mistral.ai"
    )

async def add_system_prompt(prompt: str) -> list :
    return [
        {
            "role": "system",
            "content": "You're a happy dolphin living in ocean."
        },
        {
            "role": "user",
            "content": prompt
        }
    ]

async def send_prompt(model_id: str, history: dict):
    try:
        response = await model.chat.complete_async(model=model_id,
                messages= history,
                #tools= tools,
                #tool_choice= "auto"
            )
    except Exception as e:
        return {
            "succeed": False,
            "message" : str(e)
        }
    else:
        return {
            "succeed" : True,
            "message" : response.choices[0].message.content
        }