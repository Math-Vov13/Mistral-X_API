from pydantic import BaseModel
from mistralai import BaseModelCard, ModelCapabilities
from mistralai import ChatCompletionResponse, ToolCall, ToolMessage, CompletionChunk


### Sessions
Session_id_Scheme = int
class newSession(BaseModel):
    __tablename__ = "Session"
    
    session_id: Session_id_Scheme
    created: float
    history: dict | None = None

    class Config:
        json_scheme_extra = {
            "example": {
                "session_id": 0,
                "created": 0.0,
                "history": {}
            }
        }


### Messages
Message_id_Scheme = int


### Models
class list_models_scheme(BaseModel):
    Date: float
    Length: int
    Matchs: dict[str, list[BaseModelCard]]

class ModelCapabilities_Nullable(ModelCapabilities):
    completion_chat: bool | None = None
    completion_fim: bool | None = None
    function_calling: bool | None = None
    fine_tuning: bool | None = None
    vision: bool | None = None


### Mixtral
class Reponse_Error_Scheme(BaseModel):
    type: str
    msg_error: str

class Response_Scheme(BaseModel):
    succeed: bool = True
    streaming: bool = False
    message_id: Message_id_Scheme
    response: ChatCompletionResponse | ToolCall | ToolMessage | Reponse_Error_Scheme

class Streaming_Response_Scheme(BaseModel):
    message_id: Message_id_Scheme
    index: int
    chunk: CompletionChunk