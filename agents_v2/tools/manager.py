import agents_v2.types as t

from agents_v2.providers.base import BaseProvider
from agents_v2.tools.spec import ToolSpec, ToolType


from pydantic import BaseModel
class Model(t.PydanticFormatType):
    tool_name: str
    parameters: dict

class ToolManager:
    
    def __init__(
        self,
        *,
        ai: BaseProvider,
        toolspec: ToolSpec,
        tooltype: ToolType

    ):
        self.ai = ai
        self.toolspec = toolspec
        self.tooltype = tooltype
       
    @property
    def toolparam_prompt(self) -> tuple[str, str]:
        return (
"""

""", 
"""

"""
        )
    
    @property
    def choosen_model(self) -> str:
        model = "gpt-4o-mini"
        if self.ai.provider_name == "openai":
            model = "gpt-4o-mini"
        return model

    async def _setup_toolparam(
        self
    ):
        rsp = await self.ai.ainvoke(
            instructions=self.toolparam_prompt[0],
            prompt=self.toolparam_prompt[1],
            history=None,
            model=self.choosen_model,
            response_fmt=self.toolspec.parameters
        )


    
    async def arun(
        self,
        fn
    ) -> ToolResponse:
        ...