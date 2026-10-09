from enum import Enum


class SupportedLLMs(str, Enum):
    """
    A enum of supported LLMs for the endpoint parameter.
    """

    GEMINI = "gemini/gemini-2.5-flash"
    GEMINI_LITE = "gemini/gemini-2.5-flash-lite"
    GEMINI3_LITE = "gemini/gemini-3.1-flash-lite"


class DangerAlerts(str, Enum):
    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"
