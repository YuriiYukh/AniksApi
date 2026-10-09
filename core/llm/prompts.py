JOKE_PROMPT = (
    "Write one short, original and clean joke. "
    "Return only the joke itself, without any additional comments."
)


def format_message(role: str, prompt: str) -> list[dict]:
    """
    Formats a messages for litellm completion method.
    """
    return [
        {
            "role": role,
            "content": prompt,
        }
    ]


class RecipePrompt:
    """
    Logic for handling Recipe LLM prompts
    """

    @staticmethod
    def get_ingredients_prompt(ingredients: list[str]):
        """
        Returns formatted prompt for the ingredients LLM request.
        """
        return f"""
            You are a skilled cook with a lot of knowledge about simple and efficient recipes.
            I need you to give me a simple recipe, based on ingredients, which I will send you.
            It is mostly everything that I have in my fridge, so try not to add anything else, except some spices or sauces.

            # Here is the list of ingredients:
            {RecipePrompt._format_ingredients(ingredients)}

            If needed, you can ignore some of the ingredients.
            """

    @staticmethod
    def _format_ingredients(ingredients: list[str]) -> str:
        """
        Returns formatted list of ingredients for the prompt.
        """
        formatted_ingredients = ""
        for index, ingredient in enumerate(ingredients):
            formatted_ingredients += f"{index + 1}. {ingredient}\n"
        return formatted_ingredients


class AirRaidPrompt:
    """
    Logic for handling the air raid alerts request for LLM.
    """

    @staticmethod
    def get_air_raid_prompt(tg_messages: dict, alerts_for_llm: dict | None) -> str:
        """
        Returns a formatted prompt for air raid alerts for Kyiv
        """
        return f"""
        You are a helpful home assistant, which analyses the messages from the telegram channels to inform the user about air raid alerts.
        The input contains the JSON with timedelta_messages and last_messages, filtered for Kyiv. timedelta_messages are the messages from 3 Telegram channels for last 5 minutes.
        
        last_messages - is the last messages with any alerts from those channels.
        
        I need you to analyse this dictionary and tell me if there any imminent danger for Kyiv, and if there is some - I need you to specify what is the reason of the danger
        and what channel (or channels) is the source of the information.
        
        Here is the Telegram json:
        {tg_messages}
        
        Also, include in your response the air alert status from the dict, claimed from the alerts api:
        {alerts_for_llm}
        
        If None provided - specify that.
        Also, analyse the current information about air targets movement and try to predict if UAVs or rockets will move to the Kyiv in a few hours from now. Give a quick analysis.
        
        """


class ChatInterestPrompt:
    """
    Logic for handling the chat interest prompt.
    """

    @staticmethod
    def get_interest_prompt(
        chat_dump: dict, topics: str = "", extra_instructions: str = ""
    ) -> str:
        """
        Returns a formatted prompt for the chat digest.
        Topics and extra instructions are optional and come from the settings.
        """
        topics_section = (
            f"Focus on discussions related to: {topics}." if topics else ""
        )
        return f"""
    **System**
    You are an assistant that summarises group chat discussions for a busy reader.

    **Task**
    Analyse the chat dump (the latest messages) and report only the decisions that have been made
    and the actions that are required from the reader. Ignore general discussion, opinions and off-topic messages.
    {topics_section}
    {extra_instructions}

    **Data**
    {chat_dump}

    **Output format**
    Make the output satisfy the format of this Pydantic model:

    class ChatOverview(BaseModel):
        is_interesting: bool
        details: str

    If there is nothing worth the reader's attention, is_interesting must be False and details an empty string.
    Otherwise, is_interesting must be True and details must explain what was decided and what actions are required.
    """
