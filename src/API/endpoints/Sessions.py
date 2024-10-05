from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from datetime import datetime
from random import randint
from json import dumps

from mistralai import ChatCompletionRequest, AgentsCompletionRequest
from src.API.endpoints.Models import chat_withModel
from src.Models.Mistralai.utilities import Response_Schema

router = APIRouter(prefix= "/sessions", tags= ["Sessions"])


Session_id_Schema = int
class newSession(BaseModel):
    session_id: Session_id_Schema
    created: float
    history: dict | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": 0,
                "created": 0.0,
                "history": {}
            }
        }

sessions_list = {}


## Fonctions internes
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
async def generate_message_id() -> int:
    return randint(1, 1000) ## TODO a modifier

async def delete_message(message_id: int):
    return None ## TODO a modifier

async def get_message_by_id(message_id: int) -> None:
    return None ## TODO a modifier


### GET
@router.get("/",
            summary= "List all open sessions",
            description= "<b>List of all open sessions.</b>")
async def list_all_sessions() -> dict[Session_id_Schema, newSession]:
    sessions = await get_sessions()
    if sessions is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail      = "You need to create a session_id first.",
                            headers     = {"code_error": "404", "method": "GET"})
    
    return sessions


@router.get("/{session_id}", response_model= newSession,
            summary= "Show a Session",
            description= "<b>Show a Session with its unique `session_id`.</b>")
async def retrieve_Session(session_id: int) -> newSession:
    my_session = await get_session_by_id(session_id)
    if my_session is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
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
@router.post("/{session_id}/models/completions",
             summary= "Chat with Model using a Session",
             description= "<b>Chat with the model of your choice!</b></br> The session saves your History and gives models a memory of your last exchanges.")
async def chat_withModel_Session(session_id: int, request: ChatCompletionRequest) -> Response_Schema:
    actual_session = await get_session_by_id(session_id)
    if actual_session is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail      = "The Session does not exists or has been permanently deleted",
                            headers     = {"session_id": dumps(session_id), "model_id": dumps(request.model if "model" in request else None), "code_error": "404", "method": "POST"})

    response = await chat_withModel(request= request)
    if not isinstance(response, StreamingResponse):
        response["message_id"] = await generate_message_id()

    # TODO ajouter le chat dans la session en cours
    # TODO l'id du message n'est pas envoyé quand la réponse est en Streaming ==> créer un cookie
    return response


#/// Agents
@router.post("/{session_id}/models/agents/completions",
             summary= "Chat with your Agent using a Session",
             description= "<b>Chat with one of your agents!</b></br> The session saves your History and gives agents a memory of your last exchanges.")
async def chat_withAgent_Session(session_id: int, request: AgentsCompletionRequest) -> str:
    actual_session = await get_session_by_id(session_id)
    if actual_session is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail      = "The Session does not exists or has been permanently deleted",
                            headers     = {"session_id": dumps(session_id), "agent_id": dumps(request.agent_id), "code_error": "404", "method": "POST"})

    # TODO ajouter le chat dans la session en cours
    raise HTTPException(status_code = status.HTTP_501_NOT_IMPLEMENTED,
                        detail      = "This feature has not been implemented yet.",
                        headers     = {"session_id": dumps(session_id), "agent_id": dumps(request.agent_id), "code_error": "501","method": "POST"})
    return await chat_withModel(model_id= agent_id, prompt= prompt)



### DELETE
@router.delete("/{session_id}",
               summary= "Delete a Session",
               description= "<b>Delete a Session permanently!</b></br> After this action, you will no longer be able to retrive your session history.")
async def delete_Session(session_id: int):
    if not await get_session_by_id(session_id):
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail      = "The Session does not exists or has been permanently deleted",
                            headers     = {"session_id": dumps(session_id), "code_error": "404", "method": "DELETE"})
    
    return {
        "session": await delete_session(session_id),
        "msg": "Succesfully deleted !",
        "deleted": True,
        "date": datetime.now().timestamp()
    }

@router.delete("/{session_id}/{message_id}",
               summary="Delete a Message",
               description="<b>Delete a Message from a Session permanently!</b></br> After this action, you will no longer be able to retrive this message in your session history.")
async def delete_message(session_id: int, message_id: int):
    if not await get_session_by_id(session_id):
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail      = "The Session does not exists or has been permanently deleted",
                            headers     = {"session_id": dumps(session_id), "code_error": "404", "method": "DELETE"})
    
    raise HTTPException(status_code = status.HTTP_501_NOT_IMPLEMENTED,
                        detail      = "This feature has not been implemented yet.",
                        headers     = {"session_id": dumps(session_id), "message_id": dumps(message_id), "code_error": "501", "method": "DELETE"})
    
    if not await get_message_by_id(session_id):
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail      = "The Message does not exists or has been permanently deleted",
                            headers     = {"session_id": dumps(session_id), "message_id": dumps(message_id), "code_error": "404", "method": "DELETE"})
    
    return {
        "session": session_id,
        "message": message_id,
        "msg": "Succesfully deleted !",
        "deleted": True,
        "date": datetime.now().timestamp()
    }