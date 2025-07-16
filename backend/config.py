import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()

class Config(BaseModel):

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

    @property
    def database_url(self) -> str:
        return f"postgresql+psycopg2://{self.POSTGRES_USERNAME}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    

CONFIG = Config(
    POSTGRES_USERNAME=os.getenv("POSTGRES_USERNAME", "sdkim96"),
    POSTGRES_PASSWORD=os.getenv("POSTGRES_PASSWORD", "**********"),
    POSTGRES_HOST=os.getenv("POSTGRES_HOST", "localhost"),
    POSTGRES_PORT=os.getenv("POSTGRES_PORT", '5432'),
    POSTGRES_DB=os.getenv("POSTGRES_DB", "dashboard"),
)