import asyncio

from langchain_core.prompts import ChatPromptTemplate
from langchain_mistralai import ChatMistralAI
from pydantic import BaseModel, Field

API_KEY = "uShSeog6NTL1raQnnoVRyp9QGzjDBaua"
BASE_URL = "https://api.mistral.ai/v1"
MODEL_NAME = "mistral-small-latest"


class ProfileCheck(BaseModel):
    is_valid: bool = Field(description="Is profile acceptable")
    toxicity: float = Field(description="0 to 1 toxicity score")
    nsfw: bool = Field(description="Contains sexual content")
    spam: bool = Field(description="Contains ads or spam")
    summary: str = Field(description="Short neutral summary")


llm = ChatMistralAI(api_key=API_KEY, base_url=BASE_URL, model_name=MODEL_NAME, temperature=0.2, timeout=10)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a strict moderation system for a dating app.

Analyze user profile text and return structured data.

Rules:
- Detect toxicity, insults, aggression
- Detect sexual/NSFW content
- Detect spam or ads
- Be strict but fair

Return only structured data.""",
        ),
        ("user", "Profile:\n{profile_text}"),
    ]
)

chain = prompt | llm.with_structured_output(ProfileCheck)


async def moderate_profile(profile_text: str) -> ProfileCheck:
    return await chain.ainvoke({"profile_text": profile_text})


async def main():
    result = await moderate_profile("заходи в мой тг канал: Qaswqr")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
