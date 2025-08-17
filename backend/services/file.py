import datetime as dt
import io
import os
import json

from sqlalchemy import select, update, func, insert
from sqlalchemy.orm import Session
from openai import AsyncOpenAI
from elasticsearch import AsyncElasticsearch

from typing import Literal, Tuple, BinaryIO

import backend.db.file_tables as tbl
import backend.db.user_tables as user_tbl
import backend.models as mdl
import backend.rag as rag

import backend.utils.logger as lg
import agents.main as agents

def _upsert_vectorize_status(
    session: Session,
    request_id: str,
    file_id: str,
    status: Literal["gray", "red", "yellow", "green"],
    is_insert: bool,
    error_message: str | None = None
) -> Exception | None:
    """
    Upsert the vectorization status of a file.
    """
    stmt = (
        update(tbl.VectorizingFile)
        .where(tbl.VectorizingFile.file_id == file_id)
        .values(status=status, error_message=error_message, created_at=dt.datetime.now())
    )
    if is_insert:
        stmt = (
            insert(tbl.VectorizingFile)
            .values(
                vectorizing_id="vec-" + request_id,
                file_id=file_id,
                status=status,
                error_message=error_message
            )
        )
        
    try:
        session.execute(stmt)
        session.commit()
    except Exception as e:
        session.rollback()
        lg.logger.error(f"Error updating vectorize status for file {file_id}: {e}")
        return e

    return None


def _get_file(
    session: Session,
    user_profile: mdl.User,
    file_id: str
) -> Tuple[mdl.File, Exception | None]:
    """
    Get a file by its ID.
    """
    File = tbl.File
    Vectorize = tbl.VectorizingFile
    User = user_tbl.User
    stmt = (
        select(
            File.file_id,
            File.file_path,
            File.file_name,
            File.file_size,
            File.file_extension,
            File.file_content_type,
            User.username.label("author_name"),
            func.coalesce(Vectorize.status, 'gray').label("vectorizing_status"),
            File.created_at,
            File.updated_at,
        )
        .join(
            User,
            User.user_id == File.author_id
        )
        .outerjoin(
            Vectorize,
            Vectorize.file_id == File.file_id
        )
        .where(
            File.file_id == file_id,
            File.author_id == user_profile.user_id,
            File.is_deleted == False
        )
    )
    try:
        file = session.execute(stmt).mappings().one()
    except Exception as e:
        lg.logger.error(f"Error retrieving files: {e}")
        return mdl.File.failed(), e

    return mdl.File.model_validate(file), None



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
    File = tbl.File
    Vectorize = tbl.VectorizingFile
    User = user_tbl.User
    stmt = (
        select(
            File.file_id,
            File.file_path,
            File.file_name,
            File.file_size,
            File.file_extension,
            File.file_content_type,
            User.username.label("author_name"),
            func.coalesce(Vectorize.status, 'gray').label("vectorizing_status"),
            File.created_at,
            File.updated_at,
        )
        .join(
            User,
            User.user_id == File.author_id
        )
        .outerjoin(
            Vectorize,
            Vectorize.file_id == File.file_id
        )
        .where(
            File.author_id == user_profile.user_id,
            File.is_deleted == False
        )
    )
    try:
        files = session.execute(stmt).mappings().all()
    except Exception as e:
        lg.logger.error(f"Error retrieving files: {e}")
        return [], e

    if not files:
        return [], None
    
    return [mdl.File.model_validate(file) for file in files], None



async def vectorize_file(
    user_profile: mdl.User,
    session: Session,
    request_id: str,
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

    filedto, err = _get_file(session=session, user_profile=user_profile, file_id=file_id)
    if err:
        lg.logger.error(f"Error retrieving file {file_id}: {err}")
        err = _upsert_vectorize_status(
            session=session,
            request_id=request_id, 
            file_id=file_id, 
            status="red", 
            is_insert=False,
            error_message=f"Error vectorizing file {file_id}: {err}",
        )
        if err:
            lg.logger.error(f"Error updating vectorize status: {err}")
        
        return err

    err = _upsert_vectorize_status(
        session=session,
        request_id=request_id, 
        file_id=file_id, 
        status="yellow", 
        is_insert=True,
        error_message=None,
    )
    if err:
        lg.logger.error(f"Error updating vectorize status: {err}")
        return err

    lg.logger.info(f"File {file_id} found: {filedto.file_name}")

    pages, err = await rag.format_file(filedto.file_path)
    if err:
        lg.logger.error(f"Error vectorizing file {file_id}: {err}")
        err = _upsert_vectorize_status(
            session=session,
            request_id=request_id, 
            file_id=file_id, 
            status="red", 
            is_insert=False,
            error_message=f"Error vectorizing file {file_id}: {err}",
        )
        if err:
            lg.logger.error(f"Error updating vectorize status: {err}")
        return err


    lg.logger.info(f"Pages {len(pages)} formatted")
    documents, err = await rag.analyze(
        pages, 
        ai=agents.AsyncSimpleAgent(provider=openai), 
        file=filedto,
        split_func=rag.split_by_header
    )
    
    if err:
        lg.logger.error(f"Error analyzing documents: {err}")
        err = _upsert_vectorize_status(
            session=session,
            request_id=request_id, 
            file_id=file_id, 
            status="red", 
            is_insert=False,
            error_message=f"Error vectorizing file {file_id}: {err}",
        )
        if err:
            lg.logger.error(f"Error updating vectorize status: {err}")

        return err

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
            err = _upsert_vectorize_status(
                session=session,
                request_id=request_id, 
                file_id=file_id, 
                status="red", 
                is_insert=False,
                error_message=f"Error vectorizing file {file_id}: {err}",
            )
            if err:
                lg.logger.error(f"Error updating vectorize status: {err}")
            return err
    
    success_doc = []
    for s in success:
        doc = tbl.Document(
            document_id=s,
            file_id=file_id,
        )
        success_doc.append(doc)
    
    try:
        session.add_all(success_doc)
        session.commit()
    except Exception as e:
        lg.logger.error(f"Error adding documents to session: {e}")
        return e

    err = _upsert_vectorize_status(
        session=session,
        request_id=request_id, 
        file_id=file_id, 
        status="green", 
        is_insert=False,
        error_message=None
    )
    if err:
        lg.logger.error(f"Error updating vectorize status: {err}")
        return err
    return None 


async def delete_file(
    user_profile: mdl.User,
    session: Session,
    file_id: str
) -> Exception | None:
    lg.logger.info(f"Deleting file {file_id} for user {user_profile.user_id}!!")
    
    File = tbl.File
    Doc = tbl.Document
    stmt = (
        select(
            File.file_id,
            Doc.document_id
        ).where(
            tbl.File.file_id == file_id
        ).where(
            tbl.File.is_deleted == False
        )
        .outerjoin(
            Doc,
            Doc.file_id == File.file_id
        )
    )
    rows = session.execute(stmt).mappings().all()
    to_delete_vector = []
    for r in rows:
        if r.document_id == None:
            continue
        to_delete_vector.append(r.document_id)

    if len(to_delete_vector) > 0:
        lg.logger.info(f"Deleting {len(to_delete_vector)} documents from vector store")

        vector_client = AsyncElasticsearch(
            hosts=os.getenv("ELASTICSEARCH_HOSTS", "http://localhost:9200"),
            api_key=os.getenv("ELASTICSEARCH_API_KEY", "")
        )
        async with vector_client as client:
            vector_store = await rag.VectorStore.create(
                vector_client=client,
                embedding_service=AsyncOpenAI(),
                cache_service=rag.AsyncCacheService(),
                indexname="document",
                document_class=rag.Document
            )
            success, err = await vector_store.delete_by_ids(
                ids=to_delete_vector
            )
            if err:
                lg.logger.error(f"Error Deleting documents to vector store: {err}")

    soft_delete = (
        update(tbl.File)
        .values(is_deleted=True)
        .where(tbl.File.file_id == file_id)
    )
    session.execute(soft_delete)
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        lg.logger.error(f"Error committing session: {e}")
        return e

    return None