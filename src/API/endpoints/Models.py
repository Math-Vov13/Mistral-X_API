from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from datetime import datetime
from json import loads, JSONDecodeError, dumps
from pydantic import BaseModel

from mistralai import BaseModelCard, ModelCapabilities, ChatCompletionRequest
from src.Models.Mistralai import utilities as Mixtral_Model_Utilities
from src.Models.Mistralai.utilities import Response_Schema, Streaming_Response_Schema, models_list

router = APIRouter(prefix= "/models", tags= ["Models"])


# Définir le modèle Pydantic pour le corps de la requête
class list_models_schema(BaseModel):
    Date: float
    Length: int
    Matchs: dict[str, list[BaseModelCard]]

class ModelCapabilities_Nullable(ModelCapabilities):
    completion_chat: bool | None = None
    completion_fim: bool | None = None
    function_calling: bool | None = None
    fine_tuning: bool | None = None
    vision: bool | None = None


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
async def list_all_models(capabilities: str = Query(None)) -> list_models_schema:
    models = await get_models()
    if capabilities:
        try:
            capabilities : dict = loads(capabilities)
            validated_model = ModelCapabilities_Nullable.model_validate(capabilities)
            ## ! ATTENTION ! ##
            ## Le type __ModelCapabilities__ mettra toujours par défaut 'completion_chat' et 'function_calling' en 'True'
            ## Heureusement, tous les modèles de Mistral possèdent ces 2 capacitées par défaut. (pour l'instant...?)
        
        except JSONDecodeError as json_err:
            print("Erreur lors du décodage JSON:")
            print(json_err)
            raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST,
                                detail= "The parameter must be a valid dict !",
                                headers= {"code_error": "400", "method": "GET"})
        
        except Exception as e:
            print("Erreur globale:")
            print(e)
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST,
                                detail      = "The parameter must be a valid dict !",
                                headers     = {"code_error": "400", "method": "GET"})
        
        else:
            async def get_models_by_capabilities() -> None | dict[str, BaseModelCard]:
                new_list = dict()

                for model in models.values():
                    if all(model.capabilities.model_dump().get(k) == v for k, v in validated_model.model_dump().items() if v is not None):
                        new_list[model.id] = model

                return new_list
            models = await get_models_by_capabilities()

    if not models:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail      = "No matching Models found! (If this is not the expected behaviour, please report the problem!)",
                            headers     = {"code_error": "404", "method": "GET"})
    
    dt = {}
    for k in models.keys():
        first = k.split("-", 1)[0].title()
        if first not in dt:
            dt[first] = []
        dt[first].append(models.get(k))

    return {
        "Date": datetime.now().timestamp(),
        "Length": len(models),
        "Matchs": dt
    }


@router.get("/{model_id}", response_model= BaseModelCard, #deprecated= True,
            summary="Retrive a Model",
            description= "Retrive a Model based on its `model_id`")
async def retrieve_Model(model_id: str) -> BaseModelCard:
    model = await get_model_by_id(model_id)
    if model is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail      = "The Model does not exists or has been permanently deleted!",
                            headers     = {"model_id": dumps(model_id), "code_error": "404", "method": "GET"})
    
    return model



### POST
@router.post("/completions",
             summary="Chat with Model without using a Session",
             description= "Chat with the model of your choice !")
async def chat_withModel(request: ChatCompletionRequest) -> Response_Schema | Streaming_Response_Schema:
    """Chat with a Model"""

    if request is None:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST,
                            detail      = "Body must be provided!",
                            headers     = {"model_id": dumps(request.model), "code_error": "400", "method": "POST"})

    model = await get_model_by_id(request.model)
    if model is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                                detail  = "The Model does not exists or has been permanently deleted!",
                                headers = {"model_id": dumps(request.model), "code_error": "404", "method": "POST"})

    # TODO récupérer le Cookie
    # TODO créer un nouveau message_id
    generated_response = await Mixtral_Model_Utilities.send_prompt(
        parameters= request,
        history= request.messages if await Mixtral_Model_Utilities.contain_system_prompt(request.messages) else await Mixtral_Model_Utilities.add_system_prompt(prompt= request.messages)) # Response
    
    if generated_response["succeed"] and generated_response["streaming"]: # Handle streaming
        print(generated_response["response"], flush= True)
        return StreamingResponse(
            content= Mixtral_Model_Utilities.stream_response(generated_response["response"]),
            media_type= "text/event-stream"
        )
    
    return generated_response


### DELETE
@router.delete("/{model_id}",
               summary="Delete a Model",
               description="<b>Delete a Model from your API_key.</b></br>Don't worry ! You'll just loose access to this Model, it won't be really deleted ;)")
async def delete_Model(model_id: str):
    if not await get_model_by_id(model_id):
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail      = "The Model does not exists or has been permanently deleted!",
                            headers     = {"model_id": dumps(model_id), "code_error": "404", "method": "DELETE"})
    
    return {
        "model": await delete_model(model_id),
        "msg": f"Succesfully deleted !",
        "deleted": True,
        "date": datetime.now().timestamp()
    }