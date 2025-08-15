import io
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Tuple, BinaryIO

from azure.storage.blob.aio import ContainerClient

from backend.config import CONFIG

RAG_PATH = "rag"

@asynccontextmanager
async def get_blob(
    *,
    container_name: str | None = None, 
    conn_str: str | None = None
) -> AsyncGenerator[ContainerClient, None]:
    """
    Asynchronously retrieves a blob client for the specified container.
    
    Args:
        container_name (str): The name of the container.
        conn_str (str): The connection string for the Azure Blob Storage account.
    
    Returns:
        ContainerClient: An instance of ContainerClient for the specified container.
    """

    container_client = ContainerClient.from_connection_string(
        conn_str or CONFIG.BLOB_CONNECTION_STRING, 
        container_name or CONFIG.BLOG_CONTAINER_NAME
    )
    try:
        yield container_client
    finally:
        await container_client.close()

async def upload_file(
    file_stream: io.BytesIO | BinaryIO,
    file_name: str,
    file_extension: str = ".txt"
) -> Tuple[str, Exception | None]:
    """
    Asynchronously uploads a file to Azure Blob Storage.
    
    Args:
        file_stream (io.BytesIO): The file stream to upload.
        file_name (str): The name of the file to be uploaded.
    
    Returns:
        Tuple[str, Exception | None]: The URL of the uploaded blob or an error.
    """
    try:
        async with get_blob() as container_client:
            blob_client = container_client.get_blob_client(f"{RAG_PATH}/{file_name}.{file_extension}")
            await blob_client.upload_blob(file_stream, overwrite=True)
            endpoint = blob_client.url
    except Exception as e:
            return "", e
    return endpoint, None
