from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from json import loads, JSONDecodeError, dumps
from pydantic import BaseModel
from typing import Optional

from mistralai import Mistral, BaseModelCard, ModelCapabilities, ChatCompletionRequest
from src.Models.Mistralai import utilities as Mixtral_Model_Utilities

from os import environ as env
from dotenv import load_dotenv
load_dotenv()

router = APIRouter(prefix= "/models", tags= ["Models"])
# @router.options()
# @router.get()
# @router.head()
# @router.post()
# @router.put()
# @router.delete()
# @router.trace()


model = Mistral(
        api_key= env["MISTRAL_API_KEY"],
        server_url="https://api.mistral.ai"
    )

models_list = dict([(i.id, i) for i in model.models.list().data])

# Définir le modèle Pydantic pour le corps de la requête
class PromptRequest(ChatCompletionRequest):
    model: None


## Fonctions internes

async def get_models() -> dict[str, BaseModelCard] | None:
    return models_list

async def get_model_by_id(model_id: str) -> BaseModelCard | None:
    return models_list[model_id] if model_id in models_list else None

async def delete_model(model_id: str) -> BaseModelCard:
    return models_list.pop(model_id)



### GET
@router.get("/",
            summary="List all Models",
            description="Get a list of all models you have access. *(agents or training jobs won't be listed there !)*")
async def list_all_models(capabilities: str = Query(None)) -> dict[str, BaseModelCard]:
    models = await get_models()
    if capabilities:
        try:
            capabilities : dict = loads(capabilities)
            validated_model = ModelCapabilities.parse_obj(capabilities)
            print(validated_model)
        
        except JSONDecodeError as json_err:
            print("Erreur lors du décodage JSON:")
            print(json_err)
            raise HTTPException(status_code= 417,
                                detail= "The parameter must be a valid dict !",
                                headers= {"code_error": "404", "method": "GET"})
        
        except Exception as e:
            print("Erreur globale:")
            print(e)
            raise HTTPException(status_code= 417, detail= "The parameter must be a valid dict !")
        
        else:
            async def get_models_by_capabilities() -> None | dict[str, BaseModelCard]:
                new_list = dict()

                for model in models.values():
                    if all(model.capabilities.dict().get(k) == v for k, v in validated_model.dict().items()):
                        new_list[model.id] = model

                return new_list
            models = await get_models_by_capabilities()

    if not models:
        raise HTTPException(status_code = 404,
                            detail      = "No matching Models found! (If this is not the expected behaviour, please report the problem!)",
                            headers     = {"code_error": "404", "method": "GET"})
    
    """TODO
        {
        Date : 1312.12,
        Len: 144,
        Models : {},
        }
    """
    return models


@router.get("/{model_id}", response_model= BaseModelCard, #deprecated= True,
            summary="Retrive a Model",
            description= "Retrive a Model based on its `model_id`")
async def retrieve_Model(model_id: str) -> BaseModelCard:
    model = await get_model_by_id(model_id)
    if model is None:
        raise HTTPException(status_code = 404,
                            detail      = "The Model does not exists or has been permanently deleted!",
                            headers     = {"model_id": dumps(model_id), "code_error": "404"})
    
    return model



### POST
@router.post("/{model_id}",
             summary="Chat with Model without using a Session",
             description= "Chat with the model of your choice !")
async def chat_withModel(model_id: str, request: ChatCompletionRequest) -> str:
    """Chat with a Model"""
    
    if request is None:
        raise HTTPException(status_code = 400,
                            detail      = "Prompt must be provided!",
                            headers     = {"model_id": dumps(model_id), "code_error": "400"})
    
    model = await get_model_by_id(model_id)
    if model is None:
        raise HTTPException(status_code = 404,
                                detail  = "The Model does not exists or has been permanently deleted!",
                                headers = {"model_id": dumps(model_id), "code_error": "404"})
    
    # *Utiliser le Modèle pour envoyer la requête avec le prompt*
    return await Mixtral_Model_Utilities.send_prompt(model_id= model_id, history= await Mixtral_Model_Utilities.add_system_prompt(prompt= prompt)) # Response



### DELETE
@router.delete("/{model_id}",
               summary="Delete a Model",
               description="<b>Delete a Model from your API_key.</b></br>Don't worry ! You'll just loose access to this Model, it won't be really deleted ;)")
async def delete_Model(model_id: str):
    if not await get_model_by_id(model_id):
        raise HTTPException(status_code=404,
                            detail= "The Model does not exists or has been permanently deleted!",
                            headers= {"model_id": dumps(model_id), "code_error": "404"})
    
    return {
        "model": await delete_model(model_id),
        "message": f"Succesfully deleted !"
    }