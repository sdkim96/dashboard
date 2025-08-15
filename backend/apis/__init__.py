from fastapi import FastAPI

def init_apis(app: FastAPI) -> None:
    """
    Initialize API routes and dependencies.
    
    Args:
        app (FastAPI): The FastAPI application instance.
    """
    from backend.apis.completion import (
        COMPLETION,
    )
    from backend.apis.user import (
        USER,
    )
    from backend.apis.agents import (
        AGENTS,
    )
    from backend.apis.conversations import (
        CONVERSATIONS,
    )
    from backend.apis.tools import (
        TOOLS,
    )
    from backend.apis.recommendations import (
        RECOMMENDATIONS,
    )
    from backend.apis.file import (
        FILES,
    )

    app.include_router(USER)
    app.include_router(TOOLS)
    app.include_router(CONVERSATIONS)
    app.include_router(COMPLETION)
    app.include_router(FILES)

    app.include_router(AGENTS)
    app.include_router(RECOMMENDATIONS)