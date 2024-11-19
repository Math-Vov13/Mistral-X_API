from utils.HistoryClass import History
import requests

model_id = "open-mistral-7b"

newHistory = History([
    {
        "role": "system",
        "content": "Bonjour, je suis ravis !"
    }
])

def main():
    while True:
        newHistory.append(message= str(input("> "))) # Prompt
        # print(historic)
        try:
            print(newHistory)
            response = requests.post(url= "http://127.0.0.1:8000/api/v1/models/completions", json= {"model": model_id, "messages": newHistory.History}).json()
            if response["succeed"] == False:
                raise Exception(response["response"]["msg_error"])
            newHistory.append(response["response"]["choices"][0]["message"]["content"], "assistant")

        except Exception as e:
            print("Une erreur est survenue !")
            print(e)

        else:
            # handle response
            print(newHistory.lastResponse)
            print()

if __name__ == "__main__":
    main()