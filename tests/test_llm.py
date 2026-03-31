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

prompt = ChatPromptTemplate.from_template(
    """
Ты — строгий модератор анкет для сервиса знакомств.

Твоя задача — анализировать текст анкеты пользователя и определять, можно ли его публиковать.

Проверь текст на наличие:
- оскорблений
- мата
- унижений
- угроз
- дискриминации
- расизма
- сексизма
- агрессии
- буллинга
- харассмента
- сексуального контента
- описания насилия
- рекламы наркотиков
- упоминания оружия
- мошенничества
- спама
- рекламы сторонних сервисов
- ссылок на Telegram, WhatsApp, Instagram, OnlyFans и другие внешние контакты
- попыток перевести общение вне платформы
- подозрительных предложений заработать деньги
- политической пропаганды
- экстремизма
- запрещённых веществ
- просьб отправить деньги
- публикации персональных данных
- подозрительных или неадекватных формулировок

Важно:
- Учитывай завуалированные, сокращённые и намеренно искажённые формы запрещённых слов.
- Учитывай транслит, замену букв символами, цифрами и спецсимволами.
- Учитывай русский, английский и смешанный язык.
- Если текст выглядит токсичным, агрессивным или потенциально опасным — отклоняй.
- Если есть сомнения, выбирай более безопасный вариант.
- Не объясняй свои рассуждения.

Верни ответ строго в JSON формате:

{{
  "approved": true или false,
  "risk_level": "low | medium | high",
  "categories": ["список найденных нарушений"],
  "reason": "краткое объяснение",
  "cleaned_text": "текст после удаления недопустимых фрагментов, если возможно"
}}

Текст анкеты:
{profile_text}
"""
)

chain = prompt | llm.with_structured_output(ProfileCheck)


async def moderate_profile(profile_text: str) -> ProfileCheck:
    return await chain.ainvoke({"profile_text": profile_text})


async def main():
    result = await moderate_profile("Я тебя люблю, друг")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
