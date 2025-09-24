import enum
from typing import Generic, List, Tuple, Literal

import openai
from openai.types.responses import ResponseUsage, ResponseError

import agents_v2.providers.response as resp
import agents_v2.types as t

from agents_v2.memory.history import History
from agents_v2.providers.base import BaseProvider


class OpenAIModelEnum(str, enum.Enum):
    gpt_4o = "gpt-4o"
    gpt_4o_mini = "gpt-4o-mini"
    gpt_5_nano = "gpt-5-nano"


class OpenAIProvider(BaseProvider):

    def __init__(
        self,
        client: openai.AsyncOpenAI,
        *,
        reasoning: bool = False,
    ) -> None:
        self.client = client
        self.reasoning = reasoning

    @property
    def provider_name(self) -> Literal['openai']:
        return "openai"
    
    @property
    def reasoning_dict(self) -> dict | openai.NotGiven:
        if self.reasoning:
            return {
                "generate_summary": None,
                "effort": "minimal",
                "summary": None,
            }

        return self.default

    @property
    def default(self) -> openai.NotGiven:
        return openai.NotGiven()

    async def ainvoke(
        self,
        *,
        instructions: str,
        prompt: str | None,
        history: History | None,
        model: OpenAIModelEnum,
        response_fmt: type[t.ResponseFormatT] = str,
    ) -> resp.ProviderResponse[t.ResponseFormatT]:
        
        if prompt is None and (history is None or len(history) == 0):
            raise ValueError("Either prompt or history must be provided.")

        input_messages = self._handle_request(prompt, history)

        if issubclass(response_fmt, t.PydanticFormatType):
            parsed = await self.client.responses.parse(
                text_format=response_fmt,
                input=input_messages, #type: ignore
                instructions=instructions,
                model=model.value,
                reasoning=self.reasoning_dict, # type: ignore
            )
            output = parsed.output_parsed
            if output is None:
                output = response_fmt.default()

            usage_to_handle = parsed.usage
            error_to_handle = parsed.error

        elif issubclass(response_fmt, str):
            response = await self.client.responses.create(
                input=input_messages, #type: ignore
                instructions=instructions,
                model=model.value,
                reasoning=self.reasoning_dict, # type: ignore
            )
            output = response.output_text
            usage_to_handle = response.usage
            error_to_handle = response.error
        else:
            raise ValueError("Invalid response format type.")
        
        usage, error = self._handle_response_metadata(usage_to_handle, error_to_handle)
        

        return resp.ProviderResponse[t.ResponseFormatT](
            response=output, #type: ignore
            usage=usage, 
            error=error
        )

    async def astream(
        self
    ):
        pass

    def _handle_request(self, prompt: str | None, history: History | None) -> List[dict[str, str]]:
        msgs = []
        if history:
            msgs.extend(history.to_ai_message_like())
        
        if prompt:
            msgs.append({"role": "user", "content": prompt})
        return msgs
    

    def _handle_response_metadata(
        self, 
        usage: ResponseUsage | None,
        error_msg: ResponseError | None
    ) -> Tuple[resp.Usage | None, Exception | None]:
        output_usage = None
        output_error = None

        if usage:
            output_usage = resp.Usage(
                input_tokens=usage.input_tokens or -1,
                output_tokens=usage.output_tokens or -1,
            )
        if error_msg:
            output_error = Exception(error_msg)
        
        return output_usage, output_error