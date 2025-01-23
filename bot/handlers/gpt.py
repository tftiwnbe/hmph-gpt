from config import settings
from openai import AsyncOpenAI

# TODO: use vision if image handled
# TODO: process somehow audio and video messages
# TODO: adding files to context?
# TODO: stream responses

client = AsyncOpenAI(api_key=settings.OPENAI_TOKEN.get_secret_value())


async def generate_response(request: str) -> tuple[str | None, str, int, int]:
    chat_completion = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": request,
            }
        ],
    )
    if (
        not chat_completion.usage
        or not hasattr(chat_completion.usage, "completion_tokens")
        or not hasattr(chat_completion.usage, "prompt_tokens")
    ):
        raise ValueError("Missing usage information in the response")

    return (
        chat_completion.choices[0].message.content,
        chat_completion.model,
        chat_completion.usage.completion_tokens,
        chat_completion.usage.prompt_tokens,
    )
