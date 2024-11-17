from fastapi import APIRouter, HTTPException, status, Request, BackgroundTasks
from fastapi.responses import StreamingResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from datetime import datetime
from json import dumps
from typing import AsyncGenerator

import asyncio

from mistralai import ChatCompletionRequest, AgentsCompletionRequest
from src.API.routers.Models import chat_withModel
from src.API import database
from src.API.schema import *

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
async def list_all_sessions(request: Request) -> dict[Session_id_Schema, newSession]:
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
async def retrieve_Session(request: Request, session_id: Session_id_Schema) -> newSession:
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
async def extract_content_and_save_to_db(session_id: Session_id_Schema, message_id: Message_id_Schema, to_extract: Response_Schema | asyncio.Queue):
    json_content : str

    if isinstance(to_extract, asyncio.Queue):
        to_extract : asyncio.Queue
        chunk_content: list[dict[str, str]] = list()
        while True:
            chunk = await to_extract.get()  # Récupère un chunk depuis la file
            if chunk is None:  # Signal de fin
                break

            try:
                model = Streaming_Response_Schema.model_validate_json(chunk)
                print(type(model), model)
                chunk_content.append(model.model_dump()["chunk"])
            except Exception as e:
                print("petite erreur :", e)
            
        json_content = dumps(chunk_content)
    else:
        json_content = dumps(to_extract["response"])

    print(json_content)
    await database.update_message_by_id(session_id= session_id, message_id= message_id, message= json_content)

async def queue_generator(generator, queue):
    async for chunk in generator:
        await queue.put(chunk)  # Ajoute le chunk dans la file
        yield chunk  # Envoie le chunk au client   
    await queue.put(None)


@router.post("/{session_id}/models/completions",
             summary= "Chat with Model using a Session",
             description= "<b>Chat with the model of your choice!</b></br> The session saves your History and gives models a memory of your last exchanges.")
@limiter.limit("5/2second", per_method= True)
async def chat_withModel_Session(request: Request, session_id: Session_id_Schema, body: ChatCompletionRequest, background_task: BackgroundTasks) -> Response_Schema | list[Streaming_Response_Schema]:
    actual_session = await database.get_session_by_id(session_id)
    if actual_session is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail      = "The Session does not exists or has been permanently deleted",
                            headers     = {"session_id": dumps(session_id), "model_id": dumps(body.model if "model" in body else None), "code_error": "404", "method": "POST"})


    # TODO pré-traitement au niveau de la BDD -> récupère l'id du message qui va être généré
    # TODO hasher le message_id ? (sécurité)
    generated_message_id = await database.generate_message_id(session_id)

    request.cookies["session_id"] = session_id
    response = await chat_withModel(request= request, body= body, message_id= generated_message_id)

    queue : asyncio.Queue | None = None
    if isinstance(response, StreamingResponse):
        queue = asyncio.Queue()
        response = StreamingResponse(
            content= queue_generator(response.body_iterator, queue),
            media_type= "text/event-stream",
            status_code= 200
        )

    background_task.add_task(
        extract_content_and_save_to_db,
        session_id,
        generated_message_id,
        to_extract= queue or response) # Créer une tâche
    
    return response


#/// Agents
@router.post("/{session_id}/models/agents/completions",
             summary= "Chat with your Agent using a Session",
             description= "<b>Chat with one of your agents!</b></br> The session saves your History and gives agents a memory of your last exchanges.")
@limiter.limit("5/2second", per_method= True)
async def chat_withAgent_Session(request: Request, session_id: Session_id_Schema, body: AgentsCompletionRequest) -> None:
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
async def delete_Session(request: Request, session_id: Session_id_Schema):
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
async def delete_message(request: Request, session_id: Session_id_Schema, message_id: Message_id_Schema):
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