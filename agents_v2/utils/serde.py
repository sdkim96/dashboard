from typing import Any, cast
from pydantic import BaseModel, create_model

# 동적으로 User 모델 생성
UserModel = create_model(
    'User',
    id=(int, ...),           # 필수
    name=(str, ...),         # 필수
    email=(str, None),       # 선택 (기본값 None)
)

TYPE_MAP = {
    "string": str,
    "integer": int,
    "number": float,
    "boolean": bool,
    "array": list,
    "object": dict,
}

def _analyze_string(string_obj: dict) -> tuple:
    fmt = string_obj.get("format")
    
    return (str, ...)

def _analyze_object(obj: dict) -> dict[str, tuple]:

    properties = cast(dict | None, obj.get("properties"))
    if not properties:
        raise ValueError("The schema must have 'properties' field.")
    
    returning = {}
    for name, infodict in properties.items():
        field_type = infodict.get("type")
        if not field_type:
            raise ValueError(f"The property '{name}' must have a 'type' field.")
        
        py_type = TYPE_MAP.get(field_type)
        if not py_type:
            raise ValueError(f"Unsupported type '{field_type}' for property '{name}'.")
        
        if py_type is dict:
            py_type = _analyze_object(infodict)
        elif py_type is list:
            items = infodict.get("items")
            if not items or not isinstance(items, dict):
                raise ValueError(f"The 'items' field for array '{name}' must be a dict.")
            item_type = items.get("type")
            if not item_type or item_type not in TYPE_MAP:
                raise ValueError(f"Unsupported or missing 'type' in 'items' for array '{name}'.")
            py_type = list[TYPE_MAP[item_type]]

        is_required = name in obj.get("required", [])
        default = ... if is_required else None

        returning[name] = (py_type, default)

    return returning


def to_pydantic(schema: dict, *, model_name: str | None) -> type[BaseModel]:
    model_name = model_name or schema.get("title", "Model")
    
    fields: dict[str, tuple] = {}
    required_fields = set(schema.get("required", []))


    
