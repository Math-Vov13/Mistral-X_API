from random import randint
from src.API.schema import *
from src.Models.Mistralai.utilities import models_list

### FakeDB
sessions_list = {}


### Sessions:
async def create_session() -> Session_id_Schema:
    return randint(1, 100000000) ## TODO a modifier

async def delete_session(session_id: Session_id_Schema) -> newSession:
    return sessions_list.pop(session_id)

async def get_sessions() -> dict[Session_id_Schema, newSession] | None:
    return sessions_list if sessions_list else None

async def get_session_by_id(session_id: Session_id_Schema) -> newSession | None:
    return sessions_list[session_id] if session_id in sessions_list else None


### Messages:
async def generate_message_id(session_id: Session_id_Schema) -> Message_id_Schema:
    return randint(1, 1000) ## TODO a modifier

async def update_message_by_id(session_id: Session_id_Schema, message_id: Message_id_Schema, message: str):
    # curr_session = await get_session_by_id(session_id= session_id) # Utile ??
    curr_message = await get_message_by_id(message_id= message_id)
    print("Saved ! :D")

async def delete_message(message_id: Message_id_Schema):
    return None ## TODO a modifier

async def get_message_by_id(message_id: Message_id_Schema) -> None:
    return None ## TODO a modifier


### Models
async def get_models() -> dict[str, BaseModelCard] | None:
    return models_list

async def get_model_by_id(model_id: str) -> BaseModelCard | None:
    return models_list[model_id] if model_id in models_list else None

async def delete_model(model_id: str) -> BaseModelCard:
    return models_list.pop(model_id)