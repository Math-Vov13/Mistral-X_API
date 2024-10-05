import requests
from json import dumps, loads

from mistralai import ToolCall, ToolMessage, FunctionCall

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
    },
    {
        "type": "function",
        "function": {
            "name": "the_date",
            "description": "This function give you the date in real-time",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    }
]

def find_response_to_every_question(your_question: str) -> str:
    from random import choice
    print("Le Modèle m'a posé une question !:", your_question)
    return choice([
        "It is certain.",
        "It is decidedly so.",
        "Without a doubt.",
        "Yes, definitely.",
        "You may rely on it.",
        "As I see it, yes.",
        "Most likely.",
        "Outlook good.",
        "Signs point to yes.",
        "Reply hazy, try again.",
        "Ask again later.",
        "Better not tell you now.",
        "Cannot predict now.",
        "Concentrate and ask again.",
        "Don't count on it.",
        "My reply is no.",
        "My sources say no.",
        "Outlook not so good.",
        "Very doubtful."
    ])

def the_date() -> str:
    from datetime import datetime
    return datetime.now().date().ctime()

model_id = "mistral-large-latest"

def main():
    action_called = False
    historic = History([
        {
            "role": "system",
            "content": "Speak only in french with the user!"
        }
    ])
    
    while True:
        # 'Que sais-tu du crash boursier de 1901 ?'
        if not action_called: # Si le modèle attend la réponse d'un tool_call
            historic.append(message= str(input("> "))) # Prompt

        action_called = False
        print(str(historic))
        try:
            response = requests.post(url= "http://127.0.0.1:8000/api/v1/models/completions",
                                     json= {
                                        "model": model_id,
                                        "messages": historic.History,

                                        "tools": tools,
                                        "tool_choice": "auto"
                                     })
            
            print("Status code:", response.status_code)
            print(response.content)
            print("Headers:", response.headers)

            response_json = response.json()
            if response_json["succeed"] == False:
                raise Exception(response_json["response"]["msg_error"])
            
            # historic.append(response_json["response"]["choices"][0]["message"]["content"], "assistant")

        except Exception as e:
            print("Une erreur est survenue !")
            print(e)

        else:
            # handle response
            choices = response_json["response"]["choices"][0]["message"]
            print(response_json["response"])
            print()

            if choices["content"]:
                historic.append(choices['content'], "assistant") # ajoute à l'historique
                print(f"Réponse de [{response_json['response']['model']}]: {choices['content']}")

            elif choices["tool_calls"]:
                print("TOOL TIME !:")
                print(choices["tool_calls"])

                for tool in choices["tool_calls"]:
                    tool_called = ToolCall(
                        function= FunctionCall(
                            name= tool["function"]["name"],
                            arguments= loads(tool["function"]["arguments"])
                        ),

                        id= tool["id"],
                        type= tool["type"]
                    )

                    func = globals()[tool_called.function.name]
                    if tool_called.function.arguments: # Si il y a des arguments
                        result = func(**tool_called.function.arguments)
                    else:
                        result = func()

                    tool_response = ToolMessage(
                        content= dumps(result),
                        tool_call_id= tool_called.id,
                        name= tool_called.function.name,
                        role= "tool"
                    )
                
                action_called = True
                historic.force_append({
                    "role": "assistant",
                    "tool_calls": [tool_called.model_dump()]
                    }) # Tool_Call
                historic.force_append(tool_response.model_dump()) # Tool_Message

            else:
                print("Error ! 'Content' and 'tool_calls' are empty :(")

if __name__ == "__main__":
    main()