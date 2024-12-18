from pydantic import BaseModel
from mistralai import BaseModelCard, ModelCapabilities
from mistralai import ChatCompletionResponse, ToolCall, ToolMessage, CompletionChunk
from mistralai import ChatCompletionRequest, AgentsCompletionRequest

from src.Schemas.sessions import Message_id_Schema


### Models
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


### Mixtral
#### Requests
Request_Chat_Model = ChatCompletionRequest
Request_Chat_Agent = AgentsCompletionRequest

#### Responses
Response_Model_Description = BaseModelCard

class Reponse_Error_Schema(BaseModel):
    type: str
    msg_error: str

class Response_Schema(BaseModel):
    succeed: bool = True
    streaming: bool = False
    message_id: Message_id_Schema
    response: ChatCompletionResponse | ToolCall | ToolMessage | Reponse_Error_Schema

class Streaming_Response_Schema(BaseModel):
    message_id: Message_id_Schema
    index: int
    chunk: CompletionChunk