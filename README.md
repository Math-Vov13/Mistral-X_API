# Mistral-X API

I designed an API based on Mistral API with some features I added.

<!>
I fully respect the work of the MistralAI team,
and I'm not saying that my API is better or anything.
It's just a complement with my ideas that I propose to add.
<!>

This is my first API, made with FASTAPI
For this project, I choosed Mistral API for learn how to use it.

## Features
- Save Session History
- Token auth
- Response Streaming
- Fine-tuning ?

</br>

## Quick Start
Launch your API in few steps:

**1. Create a `virtual environment`.**</br>
```sh
pip install -r requirements.txt
```
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
2. *else:, *</br>
write random chars lmao

</br>

**3. Finally, run uvicorn server**
```sh
uvicorn main:app --reload
```

</br>

## License
MIT