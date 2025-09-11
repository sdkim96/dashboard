import enum

PROJECT_API_ENDPOINT = "/api/v1"
V2_API_ENDPOINT = "/api/v2"


API_BASE_MESSAGE = "API successfully processed."

class APIPrefix(enum.Enum):
    """
    Enum for API prefixes used for categorization or grouping of endpoints.
    """
    USER = PROJECT_API_ENDPOINT + "/user"
    AGENTS = PROJECT_API_ENDPOINT + "/agents"
    CONVERSATIONS = PROJECT_API_ENDPOINT + "/conversations"
    COMPLETION = PROJECT_API_ENDPOINT + "/completion"
    RECOMMENDATIONS = PROJECT_API_ENDPOINT + "/recommendations"
    TOOLS = PROJECT_API_ENDPOINT + "/tools"
    FILES = PROJECT_API_ENDPOINT + "/files"
    V2_COMPLETION = V2_API_ENDPOINT + "/completion"


class APITag(enum.Enum):
    """
    Enum for API tags used for categorization or grouping of endpoints.
    """
    USER = "User"
    DEFAULT = "default"
    ADMIN = "admin"
    AGENTS = "agents"
    CONVERSATIONS = "conversations"
    COMPLETION = "completion"
    RECOMMENDATIONS = "recommendations"
    TOOLS = "tools"
    FILES = "files"
    V2_COMPLETION = "v2_completion"
