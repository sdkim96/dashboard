from pydantic import BaseModel, Field

class Human(BaseModel):
    name: str = Field(..., description="The name of the human")
    age: int = Field(..., description="The age of the human")


aa = {
    "name": "Alice",
    "age": 30,
}


if __name__ == "__main__":
    print(aa['nickname'])


    