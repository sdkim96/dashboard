import uuid
from typing import Annotated

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

import backend.constants as c
import backend.deps as dp

from backend.apis import init_apis
from backend.models.api import BaseResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get(
    path="/",
    response_model=BaseResponse,
    tags=[c.APITag.DEFAULT],
    summary="Root Endpoint",
    description="Welcome endpoint for the API. Returns a welcome message.",
)
async def read_root(
    request_id: Annotated[str, Depends(dp.generate_request_id)]
) -> BaseResponse:
    return BaseResponse(
        status="success",
        message="Welcome to the API!",
        request_id=request_id,
    )

init_apis(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)