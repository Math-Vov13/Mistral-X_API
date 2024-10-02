from mistralai import Mistral, SystemMessage, ChatCompletionResponse, ChatCompletionRequest, ToolCall, ToolMessage
from mistralai import HTTPValidationError, SDKError
from os import environ as env

from pydantic import BaseModel

class Response_Schema(BaseModel):
    succeed: bool
    message_id: int
    response: ChatCompletionResponse | ToolCall | ToolMessage | dict[str, str]

model = Mistral(
        api_key= env["MISTRAL_API_KEY"],
        server_url="https://api.mistral.ai"
    )

models_list = dict([(i.id, i) for i in model.models.list().data])



##-- FUNCTIONS

async def contain_system_prompt(prompt: list[dict[str, str]]) -> bool:
    return not all(map(lambda m: not isinstance(m, SystemMessage), prompt))


async def add_system_prompt(prompt: list[dict[str, str]]) -> list :
    return [
        {
            "role": "system",
            "content": "Always assist with care, respect, and truth. Respond with utmost utility yet securely. Avoid harmful, unethical, prejudiced, or negative content. Ensure replies promote fairness and positivity." # Official Mistral system prompt : https://docs.mistral.ai/capabilities/guardrailing/
        }
    ] + prompt


async def send_prompt(history: dict, parameters: ChatCompletionRequest):
    try:
        response_formatted = await model.chat.complete_async(
            model= parameters.model,
            messages= history,

            temperature= parameters.temperature,
            top_p= parameters.top_p,
            max_tokens= parameters.max_tokens,
            min_tokens= parameters.min_tokens,

            stream= False, # pour le moment, l'API ne supporte pas le Streaming...
            stop= parameters.stop,
            random_seed= parameters.random_seed,
            response_format= parameters.response_format,

            tools= parameters.tools,
            tool_choice= parameters.tool_choice,

            safe_prompt= parameters.safe_prompt,
            
            # Server side
            retries=3,
        )
        response_dict = response_formatted.model_dump()

    except HTTPValidationError as http_err:
        print("LOGS :: <" + str(http_err) + ">", f"({http_err.__class__})")
        return {
            "succeed": False,
            "message_id": -1,
            "response": {
                "type": "HTTPValidation",
                "msg_error": str(http_err) if str(http_err) != "{}" else "HTTP Error: Your request Body caused an unexpected error ?! Please pay attention to the schema requested."
            }
        }
    
    except SDKError as sdk_err:
        print("LOGS :: <" + str(sdk_err) + ">", f"({sdk_err.__class__})")
        return {
            "succeed": False,
            "message_id": -1,
            "response": {
                "type": "SDK",
                "msg_error": str(sdk_err) if str(sdk_err) != "{}" else "SDK Error: The API cannot support streaming at the moment."
            }
        }

    except Exception as e:
        print("LOGS :: <" + str(e) + ">", f"({e.__class__})")
        return {
            "succeed": False,
            "message_id": -1,
            "response": {
                "type": "Global",
                "msg_error": str(e)
            }
        }
    
    else:
        return {
            "succeed": True,
            "message_id": -1,
            "response": response_dict
        }