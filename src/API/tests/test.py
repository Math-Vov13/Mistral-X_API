import requests
from os import environ as env

base_url = "http://127.0.0.1:8000/api/v1"


# Utilisation Normale de l'API
print("Normal")
for i in range(100):
    session_id = requests.post(url=base_url + "/sessions/").json()["session_id"]
    print("session id: ", session_id, type(session_id))

print()
print(requests.delete(url= base_url + "/sessions/" + str(session_id)).json())
print()

sessions = requests.get(url=base_url + "/sessions/").json()
print("Sessions :", sessions)
print()

models = requests.get(url= base_url + "/models/").json()
print("Models :", models)
print()

model_id = "codestral-mamba-2407"
print("Model chosen :", requests.get(url= base_url + "/models/ ").json())
print()

print(requests.post(url= base_url + "/models/" + model_id, json= {
    "prompt": "This is a test prompt"
}).json())