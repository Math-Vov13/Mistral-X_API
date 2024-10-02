import requests
import functools
import json

from utils.HistoryClass import History


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
                "required": ["your_question"]
            }
        }
    }
]

model_id = "mistral-large-latest"

def main():
    historic = History([
        {
            "role": "system",
            "content": "Speak only in french with the user!"
        }
    ])
    
    while True:
        # 'Que sais-tu du crash boursier de 1901 ?'
        historic.append(message= str(input("> "))) # Prompt
        print(str(historic))
        try:
            response = requests.post(url= "http://127.0.0.1:8000/api/v1/models/completions",
                                     json= {
                                        "model": model_id,
                                        "messages": historic.History,

                                        "tools": [tools],
                                        "tool_choice": "auto"
                                     })
            
            print("Status code:", response.status_code)
            print(response.content)
            print("Headers:", response.headers)

            response_json = response.json()
            if response_json["succeed"] == False:
                raise Exception(response_json["response"]["msg_error"])
            
            historic.append(response_json["response"]["choices"][0]["message"]["content"], "assistant")

        except Exception as e:
            print("Une erreur est survenue !")
            print(e)

        else:
            # handle response
            choices = response_json["response"]["choices"][0]["message"]
            print(response_json["response"])
            print()

            if choices["content"]:
                print(f"Réponse de [{response_json["response"]["model"]}]: {choices["content"]}")
            elif choices["tool_calls"]:
                print("TOOL TIME !:")
                print(choices["tool_calls"])
            else:
                print("Error ! 'Content' and 'tool_calls' are empty :(")

if __name__ == "__main__":
    main()