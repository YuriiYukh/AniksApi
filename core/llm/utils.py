"""
This file contains different util functions for the LLM module.
"""

import re


def clear_llm_response_text(message: str) -> str:
    """
    Clears the LLM response message from the formatting symbols.
    """
    no_markdown: str = re.sub(r"[/\*\\]", "", message)
    normalized_space: str = re.sub(r"\s+", " ", no_markdown)

    return normalized_space.strip()
