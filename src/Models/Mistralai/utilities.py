from mistralai import Mistral, SystemMessage, ChatCompletionResponse, ChatCompletionRequest, CompletionEvent
from mistralai import HTTPValidationError, SDKError
from typing import AsyncGenerator

from os import environ as env
from dotenv import load_dotenv
from src.API.schema import *

load_dotenv()

model = Mistral(
        api_key= env["MISTRAL_API_KEY"],
        server_url="https://api.mistral.ai"
    )

models_list = dict([(i.id, i) for i in model.models.list().data]) #TODO enlever ?


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


async def stream_response(async_gen: AsyncGenerator[CompletionEvent, None], message_id: Message_id_Schema = -1):
    counter = -1
    async for chunk in async_gen:
        counter += 1
        yield Streaming_Response_Schema(
            message_id= message_id,
            index= counter,
            chunk= chunk.data
        ).model_dump_json()


async def send_prompt(history: dict, parameters: ChatCompletionRequest, message_id: Message_id_Schema = -1):
    try:
        if parameters.stream:
            streaming_formatted = await model.chat.stream_async(
                model= parameters.model,
                messages= history,

                temperature= parameters.temperature,
                top_p= parameters.top_p,
                max_tokens= parameters.max_tokens,

                stream= True,
                stop= parameters.stop,
                random_seed= parameters.random_seed,
                response_format= parameters.response_format,

                tools= parameters.tools,
                tool_choice= parameters.tool_choice,

                safe_prompt= parameters.safe_prompt,
                
                # Server side
                retries=3,
            )

            response_dict = streaming_formatted

        else:
            response_formatted : ChatCompletionResponse = await model.chat.complete_async(
                model= parameters.model,
                messages= history,

                temperature= parameters.temperature,
                top_p= parameters.top_p,
                max_tokens= parameters.max_tokens,

                stream= False,
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

    except (HTTPValidationError, SDKError) as http_err:
        print("LOGS :: <" + str(http_err) + ">", f"({http_err.__class__})")
        return {
            "succeed": False,
            "streaming": False,
            "message_id": -1,
            "response": {
                "type": http_err.__class__.__name__,
                "msg_error": str(http_err) if str(http_err) != "{}" else "ERROR: The MistralAI API returned an unexpected error. Verify your request Body and retry later!"
            }
        }

    except Exception as e:
        print("LOGS :: <" + str(e) + ">", f"({e.__class__})")
        return {
            "succeed": False,
            "streaming": False,
            "message_id": -1,
            "response": {
                "type": "Global",
                "msg_error": str(e)
            }
        }
    
    else:
        return {
            "succeed": True,
            "streaming": parameters.stream,
            "message_id": message_id,
            "response": response_dict
        }