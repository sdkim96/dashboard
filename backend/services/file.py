import datetime as dt
import io
import os
import json

from sqlalchemy import select
from sqlalchemy.orm import Session
from openai import AsyncOpenAI
from elasticsearch import AsyncElasticsearch

from typing import Tuple, BinaryIO

import backend.db.file_tables as tbl
import backend.models as mdl
import backend.rag as rag

import backend.utils.logger as lg
import agents.main as agents


async def upload_file(
    file_id: str,
    filename: str,
    file_size: int,
    file_content_type: str,
    file_stream: io.BytesIO | BinaryIO,
    user_profile: mdl.User,
    session: Session
) -> Exception | None:
    """
    Upload a file to the server.
    """
    name, ext = filename.split(".") if "." in filename else (filename, "txt")
    url, err = await rag.upload_file(file_stream=file_stream, file_name=file_id, file_extension=ext)
    if err:
        lg.logger.error(f"Error uploading file: {err}")
        return err
    
    new_file = tbl.File(
        file_id=file_id,
        file_path=url,
        file_name=name,
        file_size=file_size,
        file_extension=ext,
        file_content_type=file_content_type,
        author_id=user_profile.user_id,
        is_deleted=False,
        created_at=dt.datetime.now(),
        updated_at=dt.datetime.now(),
    )
    session.add(new_file)
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error committing session: {e}")
        return e
    
    return None


def get_files(
    user_profile: mdl.User,
    session: Session
) -> Tuple[list[mdl.File], Exception | None]:
    """
    Get a list of files uploaded by the user.
    """
    stmt = select(
        tbl.File
    ).where(
        tbl.File.author_id == user_profile.user_id,
        tbl.File.is_deleted == False
    )
    try:
        files = session.execute(stmt).scalars().all()
    except Exception as e:
        lg.logger.error(f"Error retrieving files: {e}")
        return [], e

    if not files:
        return [], None
    
    return [mdl.File.model_validate(file) for file in files], None



async def vectorize_file(
    user_profile: mdl.User,
    session: Session,
    file_id: str
) -> Exception | None:
    lg.logger.info(f"Vectorizing file {file_id} for user {user_profile.user_id}!!")

    openai = AsyncOpenAI()
    vector_client = AsyncElasticsearch(
        hosts=os.getenv("ELASTICSEARCH_HOSTS", "http://localhost:9200"),
        api_key=os.getenv("ELASTICSEARCH_API_KEY", "")
    )
    cache = rag.AsyncCacheService()
    indexname = "document"

    stmt = select(tbl.File).where(tbl.File.file_id == file_id)
    file = session.execute(stmt).scalar_one_or_none()
    if not file:
        lg.logger.error(f"File {file_id} not found for user {user_profile.user_id}")
        return None

    filedto = mdl.File.model_validate(file)
    lg.logger.info(f"File {file_id} found: {filedto.file_name}")

    pages, err = await rag.format_file(filedto.file_path)
    if err:
        lg.logger.error(f"Error vectorizing file {file_id}: {err}")
        return err

    lg.logger.info(f"Pages {len(pages)} formatted")
    documents, err = await rag.analyze(
        pages, 
        ai=agents.AsyncSimpleAgent(provider=openai), 
        file=filedto,
        split_func=rag.split_by_header
    )
    lg.logger.info(f"Documents {len(documents)} analyzed")

    lg.logger.info(f"Adding {len(documents)} documents to vector store")
    async with vector_client as client:
        vector_store = await rag.VectorStore.create(
            vector_client=client,
            embedding_service=openai,
            cache_service=cache,
            indexname=indexname,
            document_class=rag.Document
        )
        success, err = await vector_store.add_documents(documents)
        if err:
            lg.logger.error(f"Error adding documents to vector store: {err}")
    
    success_doc = []
    for s in success:
        doc = tbl.Document(
            document_id=s,
            file_id=file_id,
        )
        success_doc.append(doc)
    
    try:
        session.add_all(success_doc)
    except Exception as e:
        lg.logger.error(f"Error adding documents to session: {e}")
        return e

    return None 