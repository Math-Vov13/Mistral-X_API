from fastapi import APIRouter, HTTPException, status, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from datetime import datetime
from json import dumps

from mistralai import ChatCompletionRequest, AgentsCompletionRequest
from src.API.endpoints.Models import chat_withModel
from src.API import database
from src.API.scheme import *

router = APIRouter(prefix= "/sessions", tags= ["Sessions"])
limiter = Limiter(
    key_func= get_remote_address,
    strategy= "fixed-window",
    storage_uri= "memory://" #sauvegarde dans la mémoire (peut être connecté à une bdd)
)



### GET
@router.get("/",
            summary= "List all open sessions",
            description= "<b>List of all open sessions.</b>")
@limiter.limit("1/second", per_method= True)
async def list_all_sessions(request: Request) -> dict[Session_id_Scheme, newSession]:
    sessions = await database.get_sessions()
    if sessions is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail      = "You need to create a session_id first.",
                            headers     = {"code_error": "404", "method": request.method})
    
    return sessions


@router.get("/{session_id}", response_model= newSession,
            summary= "Show a Session",
            description= "<b>Show a Session with its unique `session_id`.</b>")
@limiter.limit("1/second", per_method= True)
async def retrieve_Session(request: Request, session_id: Session_id_Scheme) -> newSession:
    my_session = await database.get_session_by_id(session_id)
    if my_session is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail      = "The Session does not exists or has been permanently deleted",
                            headers     = {"session_id": dumps(session_id), "code_error": "404", "method": "GET"})
    
    ##  TODO Retourner un document txt avec l'historique de la Session ?
    return my_session



### POST
@router.post("/",
             summary= "Create a Session",
             description= "<b>Create automatically a new Session.</b>")
@limiter.limit("1/3second", per_method= True)
async def create_Session(request: Request) -> newSession:
    """Create a new Session"""
    
    NEW_session_id = await database.create_session()
    database.sessions_list[NEW_session_id] = newSession(session_id= NEW_session_id, created=datetime.now().timestamp())

    return await retrieve_Session(request= request, session_id= NEW_session_id)


#/// Models
@router.post("/{session_id}/models/completions",
             summary= "Chat with Model using a Session",
             description= "<b>Chat with the model of your choice!</b></br> The session saves your History and gives models a memory of your last exchanges.")
@limiter.limit("5/2second", per_method= True)
async def chat_withModel_Session(request: Request, session_id: Session_id_Scheme, body: ChatCompletionRequest) -> Response_Scheme:
    actual_session = await database.get_session_by_id(session_id)
    if actual_session is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail      = "The Session does not exists or has been permanently deleted",
                            headers     = {"session_id": dumps(session_id), "model_id": dumps(body.model if "model" in body else None), "code_error": "404", "method": "POST"})

    response = await chat_withModel(request= request, body= body, session_id= session_id)
    # if not isinstance(response, StreamingResponse):
    #     response["message_id"] = await generate_message_id()

    # TODO ajouter le chat dans la session en cours
    # TODO l'id du message n'est pas envoyé quand la réponse est en Streaming ==> créer un cookie
    return response


#/// Agents
@router.post("/{session_id}/models/agents/completions",
             summary= "Chat with your Agent using a Session",
             description= "<b>Chat with one of your agents!</b></br> The session saves your History and gives agents a memory of your last exchanges.")
@limiter.limit("5/2second", per_method= True)
async def chat_withAgent_Session(request: Request, session_id: Session_id_Scheme, body: AgentsCompletionRequest) -> None:
    actual_session = await database.get_session_by_id(session_id)
    if actual_session is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail      = "The Session does not exists or has been permanently deleted",
                            headers     = {"session_id": dumps(session_id), "agent_id": dumps(body.agent_id), "code_error": "404", "method": "POST"})

    # TODO ajouter le chat dans la session en cours
    raise HTTPException(status_code = status.HTTP_501_NOT_IMPLEMENTED,
                        detail      = "This feature has not been implemented yet.",
                        headers     = {"session_id": dumps(session_id), "agent_id": dumps(body.agent_id), "code_error": "501","method": "POST"})
    return await chat_withModel(model_id= agent_id, prompt= prompt)



### DELETE
@router.delete("/{session_id}",
               summary= "Delete a Session",
               description= "<b>Delete a Session permanently!</b></br> After this action, you will no longer be able to retrive your session history.")
@limiter.limit("1/5second", per_method= True)
async def delete_Session(request: Request, session_id: Session_id_Scheme):
    if not await database.get_session_by_id(session_id):
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail      = "The Session does not exists or has been permanently deleted",
                            headers     = {"session_id": dumps(session_id), "code_error": "404", "method": "DELETE"})
    
    return {
        "session": await database.delete_session(session_id),
        "msg": "Succesfully deleted !",
        "deleted": True,
        "date": datetime.now().timestamp()
    }


@router.delete("/{session_id}/{message_id}",
               summary="Delete a Message",
               description="<b>Delete a Message from a Session permanently!</b></br> After this action, you will no longer be able to retrive this message in your session history.")
@limiter.limit("1/2second", per_method= True)
async def delete_message(request: Request, session_id: Session_id_Scheme, message_id: Message_id_Scheme):
    if not await database.get_session_by_id(session_id):
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