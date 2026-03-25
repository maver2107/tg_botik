from langchain_core.prompts import ChatPromptTemplate
from langchain_mistralai import ChatMistralAI

from src.config import settings

llm = ChatMistralAI(
    api_key=settings.API_KEY, base_url=settings.BASE_URL, model_name=settings.MODEL_NAME, temperature=0.2, timeout=10
)

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
