from typing import List

from pydantic import BaseModel, Field, create_model

from backend.models import Attribute

def _to_pydantic_model(self, output_schema: List[Attribute]) -> type[BaseModel]:

    kwargs = {}
    for attr in output_schema:
        kwargs[attr.attribute] = (eval(attr.type), Field(
            ...,
            description=f"{attr.attribute} of the output schema",
            examples=[f"example of {attr.attribute}"]
        ))

    Model = create_model(
        f"OutputSchema",
        __base__=BaseModel,
        **kwargs,
    )
    return Model