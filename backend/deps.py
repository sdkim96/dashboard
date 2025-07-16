import uuid
from typing import Annotated, Generator

from sqlalchemy.orm import Session

import backend.db.engine as db

def generate_request_id() -> str:
    """
    Generates a unique request ID for tracking purposes.

    Returns:
        str: A unique request ID.
    
    """
    return str(uuid.uuid4())


def get_current_username() -> str:
    """
    Dependency to get the current username.

    Returns:
        str: The username of the current user.
    
    """
    # This is a placeholder. In a real application, you would retrieve the username from the request context.
    return "current_user"


def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get a database session.

    Yields:
        Session: A database session.
    
    """
    session = db.SessionLocal()
    try:
        yield session
    finally:
        session.close()