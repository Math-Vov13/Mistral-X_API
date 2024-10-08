from random import randint
from src.API import schema
from src.Models.Mistralai.utilities import models_list

### DataSets
sessions_list = {}


### Sessions:
async def create_session() -> schema.Session_id_Schema:
    return randint(1, 100000000) ## TODO a modifier

async def delete_session(session_id: schema.Session_id_Schema) -> schema.newSession:
    return sessions_list.pop(session_id)

async def get_sessions() -> dict[schema.Session_id_Schema, schema.newSession] | None:
    return sessions_list if sessions_list else None

async def get_session_by_id(session_id: schema.Session_id_Schema) -> schema.newSession | None:
    return sessions_list[session_id] if session_id in sessions_list else None


### Messages:
async def generate_message_id(session_id: schema.Session_id_Schema) -> schema.Message_id_Schema:
    return randint(1, 1000) ## TODO a modifier

async def delete_message(message_id: schema.Message_id_Schema):
    return None ## TODO a modifier

async def get_message_by_id(message_id: schema.Message_id_Schema) -> None:
    return None ## TODO a modifier


### Models
async def get_models() -> dict[str, schema.BaseModelCard] | None:
    return models_list

async def get_model_by_id(model_id: str) -> schema.BaseModelCard | None:
    return models_list[model_id] if model_id in models_list else None

async def delete_model(model_id: str) -> schema.BaseModelCard:
    return models_list.pop(model_id)