from mistralai import Mistral
from os import environ as env
import asyncio

from HistoryClass import History

model = Mistral(
        api_key= env["MISTRAL_API_KEY"],
        server_url="https://api.mistral.ai"
    )

tools = [
    {
        "type": "function",
        "function": {
            "name": "find_response_to_every_question",
            "description": "All you want to know, I have the answer for you !",
            "parameters": {
                "type": "object",
                "properties": {
                    "your_question": {
                        "type": "string",
                        "description": "The question you have",
                    }
                },
                "required": ["your_question"],
            },
        },
    },
]

print("Models :", model.models.list())
print()
embed = model.embeddings.create(inputs="Bonjour, traduis cette phrase", model="mistral-embed")
# print("Embedding :", model.embeddings.create(inputs="a", model="mistral-embed"))
# print()

async def main():
    historic = History([
            {
                "role": "system",
                "content": "Speak french !"
            }
        ])
    
    while True:
        prompt = str(input("> "))
        if prompt == "Hello, World!":
            print("Ajouté !")
            prompt = str(embed.data)

        historic.append(message= prompt) # Prompt
        # print(historic)
        try:
            response = await model.chat.complete_async(model="open-mixtral-8x22b",
                messages= historic.History,
                #tools= tools,
                #tool_choice= "auto"
            )
            historic.append(response.choices[0].message.content or response.choices[0].message.tool_calls, "assistant")

        except Exception as e:
            print("Une erreur est survenue !")
            print(e)

        else:
            # handle response
            choices = response.choices[0].message
            print(choices)
            print()

            if choices.tool_calls:
                print("Tools appelés :")
            else:
                print(f"Réponse de [{response.model}]: {choices.content}")

asyncio.run(main=main())