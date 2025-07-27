def init_db():
    """
    Initializes the database by creating all tables.
    """
    from backend.db.engine import engine
    from backend.db.agent_tables import create_agent_all
    from backend.db.tools_tables import create_tool_all
    from backend.db.conversations_tables import create_conversations_all
    from backend.db.user_tables import create_user_all
    from backend.db.recommendation_tables import create_recommendations_all

    create_agent_all(engine)
    create_tool_all(engine)
    create_conversations_all(engine)
    create_user_all(engine)
    create_recommendations_all(engine)


def drop_all():
    """
    Drops all tables in the database.
    """
    from backend.db.engine import engine
    from backend.db.agent_tables import drop_agent_all
    from backend.db.tools_tables import drop_tool_all
    from backend.db.conversations_tables import drop_conversations_all
    from backend.db.user_tables import drop_user_all
    from backend.db.recommendation_tables import drop_recommendations_all

    drop_agent_all(engine)
    drop_tool_all(engine)
    drop_conversations_all(engine)
    drop_user_all(engine)
    drop_recommendations_all(engine)