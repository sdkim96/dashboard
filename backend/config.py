import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()

class Config(BaseModel):

    CURRENT_ENV: str = Field(
        os.getenv("CURRENT_ENV", ""),
        description="Current environment for the application, e.g., 'dev', 'prod'.",
        examples=["dev", "prod"]
    )

    POSTGRES_USERNAME: str = Field(
        os.getenv("POSTGRES_USERNAME", "sdkim96"),
    )
    POSTGRES_PASSWORD: str = Field(
        os.getenv("POSTGRES_PASSWORD", "**********"),
    )
    POSTGRES_HOST: str = Field(
        os.getenv("POSTGRES_HOST", "localhost"),
    )
    POSTGRES_PORT: str = Field(
        os.getenv("POSTGRES_PORT", '5432'),
    )
    POSTGRES_DB: str = Field(
        os.getenv("POSTGRES_DB", "dashboard"),
    )
    GO_AGENTS_URL: str = Field(
        os.getenv("GO_AGENTS_URL", "http://localhost:8080"),
        description="URL for the Go Agents service.",
        examples=["http://localhost:8080", "https://goagents.example.com"]
    )


    @property
    def database_url(self) -> str:
        return f"postgresql+psycopg2://{self.POSTGRES_USERNAME}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    @property
    def go_searchagents_url(self) -> str:
        return self.GO_AGENTS_URL + "/api/v1/recommend/agents"

CONFIG = Config(
    CURRENT_ENV=os.getenv("CURRENT_ENV", ""),
    POSTGRES_USERNAME=os.getenv("POSTGRES_USERNAME", "sdkim96"),
    POSTGRES_PASSWORD=os.getenv("POSTGRES_PASSWORD", "**********"),
    POSTGRES_HOST=os.getenv("POSTGRES_HOST", "localhost"),
    POSTGRES_PORT=os.getenv("POSTGRES_PORT", '5432'),
    POSTGRES_DB=os.getenv("POSTGRES_DB", "dashboard"),
    GO_AGENTS_URL=os.getenv("GO_AGENTS_URL", "http://localhost:8080"),
)