import inspect
from typing import Callable, Any, List, Dict, get_origin, get_args

from pydantic import BaseModel, Field


class ToolSpec(BaseModel):
    name: str = Field(
        ...,
        description="The name of the tool.",
        examples=["search", "calculator"]
    )
    description: str = Field(
        ...,
        description="A brief description of the tool's functionality.",
        examples=["Search the web for information.", "Perform calculations."]
    )
    fn: Callable = Field(
        ...,
        description="The function to call for the tool.",
    )

class ToolResponse(BaseModel):

    name: str = Field(
        description="The name of the tool."
    )
    tool_schema: dict[str, Any] = Field(
        ...,
        description="The schema for the tool's input and output."
    )
    success: bool = Field(
        description="Indicates whether the tool invocation was successful."
    )
    output: str = Field(
        ...,
        description="The output of the tool."
    )

    @classmethod
    def failed(cls, name: str, tool_schema: dict[str, str]):
        return cls(
            name=name,
            tool_schema=tool_schema,
            success=False,
            output=""
        )


type_mapping = {
    str: "string",
    int: "integer", 
    float: "number",
    bool: "boolean",
    list: "array",
    dict: "object",
}


async def invoke_tool(tool: ToolSpec, arguments: Dict[str, Any]) -> str:
    """
    Asynchronously invokes a tool with the provided arguments.

    Args:
        tool (ToolSpec): The tool to invoke.
        *args: Positional arguments to pass to the tool.
        **kwargs: Keyword arguments to pass to the tool.

    Returns:
        Any: The result of the tool invocation.
    """
    if inspect.iscoroutinefunction(tool.fn):
        result: str = await tool.fn(**arguments)
    else:
        result: str = tool.fn(**arguments)

    return result


def to_openai_toolschema(tools: List[ToolSpec]) -> List[Dict[str, Any]]:
    """
    ToolSpec 리스트를 OpenAI function calling 스키마로 변환합니다.
    array 타입의 경우 items 속성을 자동으로 추가합니다.
    """
    # 기본 타입 매핑
    type_mapping = {
        str: "string",
        int: "integer", 
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object"
    }
    
    schemas = []
    for tool in tools:
        sig = inspect.signature(tool.fn)
        parameters = {}
        required = []
        
        for param_name, param in sig.parameters.items():
            if param.annotation != inspect.Parameter.empty:

                param_type = type_mapping.get(param.annotation, "string")
                
                if param_type == 'array':
                    origin = get_origin(param.annotation)
                    args = get_args(param.annotation)
                    
                    if origin is list and args:
                        item_type = type_mapping.get(args[0], "string")
                        parameters[param_name] = {
                            "type": "array",
                            "items": {"type": item_type}
                        }
                    else:
                        parameters[param_name] = {
                            "type": "array", 
                            "items": {"type": "string"}
                        }
                else:
                    parameters[param_name] = {"type": param_type}
                
                if param.default == inspect.Parameter.empty:
                    required.append(param_name)
            else:
                parameters[param_name] = {"type": "string"}
                if param.default == inspect.Parameter.empty:
                    required.append(param_name)
        
        schema = {
            "type": "function",
            "name": tool.name,
            "description": tool.description,
            "parameters": {
                "type": "object",
                "properties": parameters,
                "required": required
            }
        }
        schemas.append(schema)
    
    return schemas