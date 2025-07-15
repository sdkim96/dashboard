import enum

API_BASE_MESSAGE = "API successfully processed."

class APITag(enum.Enum):
    """
    Enum for API tags used for categorization or grouping of endpoints.
    """
    DEFAULT = "default"
    ADMIN = "admin"