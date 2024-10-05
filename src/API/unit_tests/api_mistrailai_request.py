from mistralai import Mistral, CompletionEvent, CompletionChunk
from os import environ as env
import asyncio
from json import loads

model = Mistral(
        api_key= env["MISTRAL_API_KEY"],
        server_url="https://api.mistral.ai"
    )

async def main():
    streaming = await model.chat.stream_async(
        model= "open-mistral-7b",
        messages= [
            {
                "role": "user",
                "content": "Bonjour !"
            }
        ],

        stream= True
    )

    async for chunk in streaming:
        print(chunk.model_dump()["data"]["choices"][0]["delta"]["content"], flush= True, end= "")

if __name__ == "__main__":
    import requests
    active_stream = True

    response = requests.post(
        url= "https://api.mistral.ai/v1/chat/completions",
        headers= {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + env["MISTRAL_API_KEY"]
            },
        json= {
            "model": "open-mistral-7b",
            "messages": [
                {
                "role": "user",
                "content": "Donne moi une liste et les ingrédients des plats français les plus connus !"
                }],
            "stream": active_stream
            },
            stream= True
        )
    
    print(response)

    if active_stream:
        for chunk in response.iter_lines(decode_unicode= True):
            # print(list(response.iter_lines()))
            if len(chunk) == 0 or chunk == "data: [DONE]": continue
            
            chunk_dict = loads(chunk[6:])
            print(chunk_dict["choices"][0]["delta"]["content"], flush= True, end= "")
    else:
        print(response.json())

    # asyncio.run(main())