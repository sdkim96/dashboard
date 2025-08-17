import json
from typing import List,  Tuple, Generic, TypeVar, cast, Any

from pydantic import BaseModel, Field, ConfigDict, create_model
from anthropic import Anthropic, AsyncAnthropic
from openai import AsyncOpenAI, OpenAI
from openai.types.chat import ChatCompletion

from agents.internal.search_engine import BaseSearchEngine

import agents.tools as tl

ProviderT = TypeVar("ProviderT", bound=OpenAI | Anthropic)
AsyncProviderT = TypeVar("AsyncProviderT", bound=AsyncOpenAI | AsyncAnthropic)

ParsedT = TypeVar("ParsedT", bound=BaseModel)

class Attribute(BaseModel):
    """
    Represents an attribute for the output schema of an agent's response.
    """
    attribute: str = Field(
        ...,
        description="attribute for the output schema",
        examples=["field1", "field2"]
    )
    type: str = Field(
        ...,
        description="type of the output schema, e.g., 'str', 'int', 'float', 'bool'.",
        examples=['str', 'int', 'float', 'bool']
    )

class AsyncSimpleAgent(Generic[AsyncProviderT]):
    def __init__(
        self, 
        provider: AsyncProviderT,
        tools: List[tl.ToolSpec] = [],
        user_context: str | None = None
    ):
        
        self.provider = provider
        self.tools = tools
        self.user_context = user_context

    async def _handle_tool_calls(
        self, 
        messages: List[dict], 
    ) -> Tuple[
            List[dict[str, str]], 
            List[tl.ToolResponse],
            Exception | None
        ]:
        tool_response = []
        schemas = tl.to_openai_toolschema(self.tools)
        schema_map = {
            s['name']: s for s in schemas
        }

        if not isinstance(self.provider, AsyncOpenAI):
            return messages, [tl.ToolResponse.failed(name=s['name'], tool_schema=s) for s in schemas], NotImplementedError("Tool calling is only implemented for AsyncOpenAI.")

        temp_messages = messages.copy()
        temp_messages.insert(
            0,
            {
                'role': 'developer',
                'content': (
"""
## 역할
당신은 좋은 답변 생성기입니다.

## 목표
사용자는 당신이 참고할 수 있는 영역에 내부 문서나 어떤 도구의 호출이 필요합니다.
사용자의 가장 최근 메시지에 가중치를 두어, <사용자 맥락> 을 고려하여 필요한 도구를 호출하십시오.

## <사용자 맥락>
{context}

""".format(context=self.user_context)
                )
            }
        )
        try:
            response = await self.provider.responses.create(
                model="gpt-5-nano",
                input=temp_messages, # type: ignore
                tools=schemas, # type: ignore,
                tool_choice="required",
                reasoning={"effort": "minimal"}
            )
        except Exception as e:
            return messages, [tl.ToolResponse.failed(name=s['name'], tool_schema=s) for s in schemas], e

        messages += response.output  # type: ignore

        for item in response.output:
            
            fn_call = None
            fn_name = None
            fn_args = None
            toolspec = None

            if item.type == 'function_call':
                
                fn_call = item
                fn_name = item.name
                fn_args = json.loads(item.arguments)

            for available in self.tools:
                if available.name == fn_name:
                    toolspec = available
                    break

            if toolspec and fn_args and fn_call:
                tool_result = await tl.invoke_tool(
                    tool=toolspec,
                    arguments=fn_args
                )
                messages.append(
                    {
                        "type": "function_call_output",
                        "call_id": fn_call.call_id,
                        "output": tool_result,
                    }
                )
                tool_response.append(
                    tl.ToolResponse(
                        name=toolspec.name,
                        tool_schema=schema_map[toolspec.name],
                        success=True,
                        output=tool_result
                    )
                )
        
        return messages, tool_response, None

    async def ainvoke(
        self,
        messages: List[dict],
        deployment_id: str,
    ) -> Tuple[str, Exception | None]:
        """
        Asynchronously invokes the agent with the provided messages and output schema.

        Args:
            messages (List[dict]): The messages to send to the agent.
            deployment_id (str): The ID of the agent's deployment.
        Returns:
            str: The response from the agent.
        """

        if isinstance(self.provider, AsyncOpenAI):
            try:
                result = cast(
                    ChatCompletion,
                    await self.provider.chat.completions.create(
                        model=deployment_id,
                        messages=messages,  # type: ignore
                    )
                )
            except Exception as e:
                return "", e
            try:
                cnt = result.choices[0].message.content
                if cnt is None:
                    return "", ValueError("No content in the response.")
                return cnt, None
            except Exception as e:
                return "", e

        elif isinstance(self.provider, AsyncAnthropic):
            raise NotImplementedError("AsyncAnthropic is not implemented yet.")

        return "", ValueError("Unsupported provider type.")


    async def aparse(
        self,
        messages: List[dict],
        response_fmt: type[ParsedT],
        deployment_id: str
    ) -> Tuple[ParsedT | None, Exception | None]:
        """
        Asynchronously parses the response from the agent based on the provided messages.

        Args:
            messages (List[dict]): The messages to send to the agent.
            output_schema (List[dict[str, str]] | None): The schema for the expected
                output. If None, the output will not be parsed.
        Returns:
            List[dict[str, str]]: The parsed response from the agent.
        """
        
        if isinstance(self.provider, AsyncOpenAI):
            response = await self.provider.responses.parse(
                model=deployment_id,
                input=messages, #type: ignore
                text_format=response_fmt
            )
        else:
            raise NotImplementedError("Parsing is not implemented for this provider.")
        
        parsed = response.output_parsed
        if not parsed:
            return None, ValueError("No parsed content in the response.")

        return parsed, None
    
    async def astream_v2(
        self,
        messages: List[dict],
        deployment_id: str
    ):
        """
        Asynchronously streams the response from the agent based on the provided messages.

        """
        (
            messages, 
            tool_responses, 
            err
        ) = await self._handle_tool_calls(messages=messages)

        schemas = [s.tool_schema for s in tool_responses if s.success]
        yield {'type': 'status', 'content': "🤖 Generating Answers..."}
        for r in tool_responses:
            yield {'type': 'tool', 'content': r.model_dump_json()}

        left_message = {
            'role': 'developer',
            'content': (
"""
## 역할
당신은 좋은 답변 생성기입니다.
만약 당신이 참고할 수 있는 영역에 내부 문서나 어떤 도구의 호출 결과가 있으면 그것을 적극적으로 사용하시오.
            
"""
            )
        }
        messages.insert(0, left_message)

        if not isinstance(self.provider, AsyncOpenAI):
            raise NotImplementedError("Streaming is not implemented for this provider.")
        try:
            async with self.provider.responses.stream(
                model=deployment_id,
                input=messages,
                tools=schemas,
            ) as stream:
                async for event in stream:
                    if event.type == 'response.output_text.delta':
                        yield {'type': 'delta', 'content': event.delta}
                    elif event.type == 'response.output_text.done':
                        yield {'type': 'done', 'content': event.text}
                    elif event.type == 'response.failed':
                        yield {'type': 'error', 'content': event.response.error.message if event.response.error else "Unknown error"}
        except Exception as e:
            yield {'type': 'error', 'content': str(e)}
            

    
    async def astream(
        self,        
        messages: List[dict],
        deployment_id: str,
    ):
        
        """
        Asynchronously streams the response from the agent based on the provided messages.

        Args:
            messages (List[dict]): The messages to send to the agent.
            deployment_id (str): The ID of the agent's deployment.
        Yields:
            dict[str, str]: The response from the agent.
        
        Yield example:
            {'type': 'delta', 'content': event.delta}
            {'type': 'done', 'content': event.content}
            {'type': 'error', 'content': str(e)}
        """
        
        if isinstance(self.provider, AsyncOpenAI):
            try:
                async with self.provider.chat.completions.stream(
                    model=deployment_id,
                    messages=messages,  # type: ignore
                ) as stream:
                    async for event in stream:
                        if event.type == 'content.delta':
                            yield {'type': 'delta', 'content': event.delta}
                        elif event.type == 'content.done':
                            yield {'type': 'done', 'content': event.content}
            except Exception as e:
                yield {'type': 'error', 'content': str(e)}

        else:
            raise NotImplementedError("Streaming is not implemented for this provider.")

    
