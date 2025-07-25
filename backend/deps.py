import uuid
from typing import Annotated, Generator

from sqlalchemy.orm import Session

import backend.db.engine as db
import backend.models.user as user_mdl

def generate_request_id() -> str:
    """
    Generates a unique request ID for tracking purposes.

    Returns:
        str: A unique request ID.
    
    """
    return str(uuid.uuid4())


def get_current_userprofile() -> user_mdl.User:
    """
    Dependency to get the current user profile.

    Returns:
        User: The user profile of the current user.
    """
    

    #TODO: Implement logic to retrieve the current user profile.
    return user_mdl.User(
        user_id="current_user_id",
        username="current_username",
        email="current_user_email",
        icon_link="https://example.com/current_user_icon.png",
        is_superuser=False,
    )


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