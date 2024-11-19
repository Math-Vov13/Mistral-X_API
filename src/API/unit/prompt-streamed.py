import httpx
from json import loads

model_id = "open-mistral-7b"

with httpx.stream(method='POST',
                  url= "http://127.0.0.1:8000/api/v1/models/completions",
                  json= {
                    "model": model_id,
                    "messages": [{
                        "role": "user",
                        "content": "Liste tous les présidents des US jusqu'à aujourd'hui."
                    }],
                    "stream": True
                  }) as r:

    for chunk in r.iter_raw():
        print(loads(chunk)["chunk"]["choices"][0]["delta"]["content"], flush= True, end= "")