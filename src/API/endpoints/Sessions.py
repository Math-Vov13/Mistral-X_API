from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from json import dumps

from mistralai import ChatCompletionRequest
from src.API.endpoints.Models import chat_withModel

router = APIRouter(prefix= "/sessions", tags= ["Sessions"])


Session_id_Schema = int
class newSession(BaseModel):
    session_id: Session_id_Schema
    created: float
    historic: dict | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": 0,
                "created": 0.0,
                "historic": {}
            }
        }

sessions_list = {}


## Fonctions internes
async def create_session() -> Session_id_Schema:
    from random import randint
    return randint(1, 100000000)

async def delete_session(session_id: Session_id_Schema) -> newSession:
    return sessions_list.pop(session_id)

async def get_sessions() -> dict[Session_id_Schema, newSession] | None:
    return sessions_list if sessions_list else None

async def get_session_by_id(session_id: Session_id_Schema) -> newSession | None:
    return sessions_list[session_id] if session_id in sessions_list else None



### GET
@router.get("/",
            summary= "List all open sessions",
            description= "<b>List of all open sessions.</b>")
async def list_all_sessions() -> dict[Session_id_Schema, newSession]:
    sessions = await get_sessions()
    if sessions is None:
        raise HTTPException(status_code = 404,
                            detail      = "You need to create a session_id first.",
                            headers     = {"code_error": "404", "method": "GET"})
    
    return sessions


@router.get("/{session_id}", response_model= newSession,
            summary= "Show a Session",
            description= "<b>Show a Session with its unique `session_id`.</b>")
async def retrieve_Session(session_id: int) -> newSession:
    my_session = await get_session_by_id(session_id)
    if my_session is None:
        raise HTTPException(status_code = 404,
                            detail      = "The Session does not exists or has been permanently deleted",
                            headers     = {"session_id": dumps(session_id), "code_error": "404", "method": "GET"})
    
    return my_session



### POST
@router.post("/",
             summary= "Create a Session",
             description= "<b>Create automatically a new Session.</b>")
async def create_Session() -> newSession:
    """Create a new Session"""

    NEW_session_id = await create_session()
    sessions_list[NEW_session_id] = newSession(session_id= NEW_session_id, created=datetime.now().timestamp())

    return await retrieve_Session(NEW_session_id)


#/// Models
# @router.post("/{session_id}/models/{model_id}",
#              summary= "Chat with Model using a Session",
#              description= "<b>Chat with the model of your choice!</b></br> The session saves your History and gives models a memory of your last exchanges.")
# async def chat_withModel_Session(session_id: int, model_id: str, prompt: str | None = None) -> str:
#     actual_session = await get_session_by_id(session_id)
#     if actual_session is None:
#         raise HTTPException(status_code = 404,
#                             detail      = "The Session does not exists or has been permanently deleted",
#                             headers     = {"session_id": dumps(session_id), "model_id": dumps(model_id), "code_error": "404", "method": "POST"})
    
#     if prompt is None:
#         raise HTTPException(status_code = 400,
#                             detail      = "Prompt must be provided!",
#                             headers     = {"session_id": dumps(session_id), "model_id": dumps(model_id), "code_error": "400","method": "POST"})

#     # TODO ajouter le chat dans la session en cours
#     return await chat_withModel(model_id= model_id, prompt= prompt)


@router.post("/{session_id}/models/completions",
             summary= "Chat with Model using a Session",
             description= "<b>Chat with the model of your choice!</b></br> The session saves your History and gives models a memory of your last exchanges.")
async def chat_withModel_Session(session_id: int, request: ChatCompletionRequest) -> str:
    actual_session = await get_session_by_id(session_id)
    if actual_session is None:
        raise HTTPException(status_code = 404,
                            detail      = "The Session does not exists or has been permanently deleted",
                            headers     = {"session_id": dumps(session_id), "model_id": dumps(model_id), "code_error": "404", "method": "POST"})
    
    # if request is None:
    #     raise HTTPException(status_code = 400,
    #                         detail      = "Prompt must be provided!",
    #                         headers     = {"session_id": dumps(session_id), "model_id": dumps(model_id), "code_error": "400","method": "POST"})

    # TODO ajouter le chat dans la session en cours
    return await chat_withModel(model_id= request.model, prompt= request.messages)


#/// Agents
@router.post("/{session_id}/models/agents/{agent_id}",
             summary= "Chat with your Agent using a Session",
             description= "<b>Chat with one of your agents!</b></br> The session saves your History and gives agents a memory of your last exchanges.")
async def chat_withAgent_Session(session_id: int, agent_id: str, prompt: str | None = None) -> str:
    actual_session = await get_session_by_id(session_id)
    if actual_session is None:
        raise HTTPException(status_code = 404,
                            detail      = "The Session does not exists or has been permanently deleted",
                            headers     = {"session_id": dumps(session_id), "agent_id": dumps(agent_id), "code_error": "404", "method": "POST"})
    
    if prompt is None:
        raise HTTPException(status_code = 400,
                            detail      = "Prompt must be provided!",
                            headers     = {"session_id": dumps(session_id), "agent_id": dumps(agent_id), "code_error": "400","method": "POST"})

    # TODO ajouter le chat dans la session en cours
    raise HTTPException(status_code = 501,
                        detail      = "This feature has not been implemented yet.",
                        headers     = {"session_id": dumps(session_id), "agent_id": dumps(agent_id), "code_error": "501","method": "POST"})
    return await chat_withModel(model_id= agent_id, prompt= prompt)



### DELETE
@router.delete("/{session_id}",
               summary= "Delete a Session",
               description= "<b>Delete a Session permanently!</b></br> After this action, you will no longer be able to retrive your sesison history.")
async def delete_Session(session_id: int):
    if not await get_session_by_id(session_id):
        raise HTTPException(status_code = 404,
                            detail      = "The Session does not exists or has been permanently deleted",
                            headers     = {"session_id": dumps(session_id), "code_error": "404", "method": "DELETE"})
    
    return {
        "session": await delete_session(session_id),
        "message": "Succesfully deleted !",
        "deleted": True,
        "date": datetime.now().timestamp()
    }