from random import randint
from src.Schemas.mistral_ai import *
from src.Models.Mistralai.utilities import models_list



### Models
async def get_models() -> dict[str, BaseModelCard] | None:
    return models_list

async def get_model_by_id(model_id: str) -> BaseModelCard | None:
    return models_list[model_id] if model_id in models_list else None

async def delete_model(model_id: str) -> BaseModelCard:
    return models_list.pop(model_id)