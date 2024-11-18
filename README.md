# Mistral-X API

<div style="border: 2px solid red; padding: 10px; border-radius: 5px;">
    <strong>⚠️ Before start, please notice :</strong>

    I fully respect the work of the MistralAI team,
    and I'm not saying that my API is better or anything.
    It's just a complement with my ideas that I propose to add.
</div>

</br>

## 📚 About the project

![MistralAI-X logo](/references/mistralai-x-fastapi.png)

**I'd like to introduce you "<u>Mistral-X API</u>", an API with new features compared to the [official](https://docs.mistral.ai/api/)**.</br>
and with my personal touch ♥

➕ **Features:**

- Save Session History
- Token auth
- Response Streaming
- Fine-tuning ?

</br>

💡 **Documentation:**

> See all endpoints [here](/API.md)

> See how to host the API [here](/HOST.md)

> See how to create your database [here](/BDD.md)

</br>


*And btw, this is my first API using FastAPI... :D*

</br>

## ⚡ Quick Start

I recommend you to create a virtual environment first
```sh
python -m venv .venv
```

---
</br>

<i>**Launch your API in a few steps! :**</i>

**1. Install dependencies**</br>
```sh
pip install -r requirements.txt
```

or, if you use **[Poetry](https://python-poetry.org/docs/basic-usage/)**:
```sh
poetry install
```

---
</br>


**2. Create a `.env` file**</br>
*This file must contain :*
```env
# go to : https://console.mistral.ai/api-keys/
# and generate an API Key

MISTRAL_API_KEY = "<mistral-api-key>"
SECRET_KEY = "<secret-key>"
```

To generate a secret key:</br>
1. *if you have openssl already installed:*
```sh
openssl rand -hex 32
```
2. *else:*</br>
write random chars lmao


---
</br>


**3. Finally, run uvicorn server**
```sh
uvicorn main:app --reload
```

or, with **[Poetry](https://python-poetry.org/docs/basic-usage/)**:
```sh
poetry run uvicorn main:app --reload
```

</br>

## 📜 License
MIT