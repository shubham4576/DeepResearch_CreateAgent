from langchain_openai import ChatOpenAI

from config import config


def make_llm(
    model: str = config.OPENAI_DEFAULT_MODEL,
    temperature: float = 0,
    reasoning: dict | None = None,
    **kwargs,
) -> ChatOpenAI:
    """
    Create and configure a ChatOpenAI instance.

    This private factory centralizes shared defaults so that changes
    such as callbacks, streaming, timeouts, or retry settings can be
    made in one place instead of updating multiple instances.

    :param model:
        Name of the OpenAI model to use.

    :param temperature:
        Sampling temperature used for generation.

    :param reasoning:
        Specify the reasoning effort none, minimal, low, medium, high, and xhigh.
        Defaults to ``none``. Example - {"effort":"low"}

    :param kwargs:
        Additional keyword arguments passed directly to ``ChatOpenAI``.
        Common options include:

        - ``max_tokens``: Maximum number of tokens to generate.
        - ``stream_options``: Streaming configuration options.
        - ``use_responses_api``: Whether to use the Responses API.
        - ``timeout``: Timeout for API requests.
        - ``max_retries``: Maximum number of retry attempts.
        - ``api_key``: OpenAI API key. Defaults to ``OPENAI_API_KEY``.
        - ``base_url``: Base URL for API requests.
        - ``organization``: OpenAI organization ID.

    :return:
        A configured ``ChatOpenAI`` instance.
    """

    return ChatOpenAI(
        model=model,
        temperature=temperature,
        api_key=config.OPENAI_API_KEY,
        reasoning=reasoning,
        **kwargs,
    )


# Use these if you do not need customized parameters
llm_gpt5 = make_llm()  # For heavy Tasks
llm_gpt5_mini = make_llm(model="gpt-5.4-mini")  # For light tasks
